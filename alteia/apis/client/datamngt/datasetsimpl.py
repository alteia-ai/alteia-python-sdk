import hashlib
import logging
import os.path
import sys
import urllib.parse
from typing import Any, Dict, Generator, List, Optional, Sequence, Union, overload

import urllib3.exceptions

from alteia.apis.provider import DataManagementAPI
from alteia.core.errors import DownloadError, ParameterError, UnsupportedResourceError
from alteia.core.resources.datamngt.uploader import DatasetUploader
from alteia.core.resources.resource import Resource, ResourcesWithTotal
from alteia.core.resources.utils import search_generator
from alteia.core.utils.requests import (
    extract_filename_from_headers,
    generate_raster_tiles_url,
    generate_vector_tiles_url,
)
from alteia.core.utils.srs import expand_vertcrs_to_wkt
from alteia.core.utils.typing import (
    AnyPath,
    Offset,
    ResourceId,
    SomeResourceIds,
    SomeResources,
)
from alteia.core.utils.utils import dict_merge, get_chunks

# TODO complete description of bands for rasters
# TODO complete description of bands for images

LOGGER = logging.getLogger(__name__)
MAX_URL_LENGTH = 2000  # Can be more for some clients (used to display a warning)
MAX_RASTER_DATASETS_PER_TILE_URL = 150  # To make sure resulting URL is < 4000 characters

__creation_common_params = (
    "name",
    "source_name",
    "categories",
    "company",
    "project",
    "mission",
    "flight",
    "hidden",
    "published",
    "horizontal_srs_wkt",
    "vertical_srs_wkt",
    "dataset_format",
    "geometry",
    "properties",
)


def _build_component_dict_list_from_names(
    components: Union[List[str], List[Dict[str, Any]]],
):
    """Turn component list into a dictionary list.

    >> _build_component_dict_list_from_names(['material', 'texture'])
    [{'name': 'material'}, {'name': 'texture'}]

    Returns:
        List of components dictionaries with at least a key
        ``name``.

    """
    component_dict_list = []
    for component in components:
        if isinstance(component, dict):
            component_dict_list.append(component)
        else:
            component_dict_list.append({"name": component})
    return component_dict_list


def _adapt_params(params: Dict[str, Any]) -> Dict[str, Any]:
    p = params.copy()

    for common_param in __creation_common_params:
        if common_param in p:
            if p[common_param] is not None:
                p[common_param] = p.pop(common_param)
            else:
                p.pop(common_param)

    if all([p.get("company") is None, p.get("project") is None]):
        raise ParameterError('One of "company" or "project" must be specified')

    if "dataset_format" in p:
        p["format"] = p.pop("dataset_format")

    if "source_name" in p:
        p["source"] = {"name": p.pop("source_name")}

    return p


class DatasetsImpl:
    def __init__(self, data_management_api: DataManagementAPI, sdk, **kwargs):
        self._provider = data_management_api
        self._sdk = sdk

    @staticmethod
    def _generate_comp_names(base_name: str, count: int) -> List[str]:
        """Return a list of component names.

        Args:
            base_name: The base name of the component names to generate.

            count: The number of component names to generate.

        Returns:
            List of component names.

        """
        if count <= 0:
            return []
        elif count == 1:
            return [base_name]
        return [f"{base_name}_{i}" for i in range(count)]

    def _create(
        self,
        dataset_type: str,
        component_names: Union[List[str], List[Dict[str, Any]]],
        **kwargs,
    ) -> Resource:
        components = _build_component_dict_list_from_names(component_names)

        if dataset_type not in (
            "file",
            "mesh",
            "image",
            "raster",
            "pcl",
            "vector",
            "file",
        ):
            raise ValueError(f'Unsupported type "{dataset_type}"')

        adapted_params = _adapt_params(kwargs)
        if "vertical_srs_wkt" in adapted_params:
            adapted_params["vertical_srs_wkt"] = expand_vertcrs_to_wkt(kwargs["vertical_srs_wkt"])

        params = {"type": dataset_type, "components": components}
        params.update(adapted_params)

        desc = self._provider.post("create-dataset", data=params)
        return Resource(**desc)

    def create_file_dataset(
        self,
        *,
        name: str,
        categories: Sequence[str] | None = None,
        company: ResourceId | None = None,
        project: ResourceId | None = None,
        mission: ResourceId | None = None,
        hidden: bool | None = None,
        published: bool | None = None,
        horizontal_srs_wkt: str | None = None,
        vertical_srs_wkt: str | None = None,
        dataset_format: str | None = None,
        geometry: dict | None = None,
        properties: dict | None = None,
        file_count: int = 1,
        components: List[str] | None = None,
        **kwargs,
    ) -> Resource:
        """Create a dataset of type ``file``.

        One of ``company`` or ``project`` must be defined.

        Args:
            name: Name of the dataset.

            categories: Sequence of categories or None if there's no
                category to set on the dataset.

            company: Optional company identifier.

            project: Optional project identifier.

            mission: Optional mission identifier.

            hidden: Whether not to display the dataset to end-users or
                not.

            published: Whether the dataset is ready for delivery or
                not.

            horizontal_srs_wkt: Optional geographic coordinate system
                for horizontal coordinattes in WKT format.

            vertical_srs_wkt: Optional geographic coordinate system
                for vertical coordinattes in WKT format.

            dataset_format: Optional file format.

            geometry: Optional geometry of the dataset.

            properties: Optional custom properties of the dataset.

            file_count: Number of files. Default to 1. It is used to generate
                the component names automatically, except if ``components`` is
                defined.

            components: Optional sequence of component names. When
                defined, ``file_count`` is ignored.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: Resource for the created dataset.

        """
        if not components:
            components = self._generate_comp_names("file", file_count)
        if not isinstance(components, list):
            raise TypeError(f"components must be a list; {type(components)!r} received")

        params = kwargs
        params.update(
            {
                "name": name,
                "categories": categories,
                "company": company,
                "project": project,
                "mission": mission,
                "hidden": hidden,
                "published": published,
                "horizontal_srs_wkt": horizontal_srs_wkt,
                "vertical_srs_wkt": vertical_srs_wkt,
                "dataset_format": dataset_format,
                "geometry": geometry,
                "properties": properties,
            }
        )
        return self._create("file", components, **params)

    def create_mesh_dataset(
        self,
        *,
        name: str,
        categories: Sequence[str] | None = None,
        company: ResourceId | None = None,
        project: ResourceId | None = None,
        mission: ResourceId | None = None,
        hidden: bool | None = None,
        published: bool | None = None,
        horizontal_srs_wkt: str | None = None,
        vertical_srs_wkt: str | None = None,
        dataset_format: str | None = None,
        geometry: dict | None = None,
        properties: dict | None = None,
        texture_count=1,
        material_count=1,
        offset: Offset | None = None,
        **kwargs,
    ) -> Resource:
        """Create a dataset of type ``mesh``.

        One of ``company`` or ``project`` must be defined.

        Args:
            name: Name of the dataset.

            categories: Sequence of categories or None if there's no
                category to set on the dataset.

            company: Optional company identifier.

            project: Optional project identifier.

            mission: Optional mission identifier.

            hidden: Whether not to display the dataset to end-users or
                not.

            published: Whether the dataset is ready for delivery or
                not.

            horizontal_srs_wkt: Optional geographic coordinate system
                for horizontal coordinattes in WKT format.

            vertical_srs_wkt: Optional geographic coordinate system
                for vertical coordinattes in WKT format.

            dataset_format: Optional file format.

            geometry: Optional geometry of the dataset.

            properties: Optional custom properties of the dataset.

            texture_count: Number of texture files. Default to 1.

            material_count: Number of materials files. Defaut to 1.

            offset: Optional translation from mesh coordinates to
                spatial coordinates.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: Resource for the created dataset.

        """
        textures = self._generate_comp_names("texture", texture_count)
        materials = self._generate_comp_names("material", material_count)
        components = ["mesh"] + textures + materials

        params = kwargs
        if offset is not None:
            params["offset"] = offset

        params.update(
            {
                "name": name,
                "categories": categories,
                "company": company,
                "project": project,
                "mission": mission,
                "hidden": hidden,
                "published": published,
                "horizontal_srs_wkt": horizontal_srs_wkt,
                "vertical_srs_wkt": vertical_srs_wkt,
                "dataset_format": dataset_format,
                "geometry": geometry,
                "properties": properties,
            }
        )

        return self._create("mesh", components, **params)

    def create_image_dataset(
        self,
        *,
        name: str,
        categories: Sequence[str] | None = None,
        company: ResourceId | None = None,
        project: ResourceId | None = None,
        mission: ResourceId | None = None,
        flight: ResourceId | None = None,
        hidden: bool | None = None,
        published: bool | None = None,
        horizontal_srs_wkt: str | None = None,
        vertical_srs_wkt: str | None = None,
        dataset_format: str | None = None,
        geometry: dict | None = None,
        properties: dict | None = None,
        acquisition_date: str | None = None,
        width: int | None = None,
        height: int | None = None,
        sensor: dict | None = None,
        lens: dict | None = None,
        camera_parameters: dict | None = None,
        reflectance_calibration_panel: dict | None = None,
        parse_metadata: bool | None = None,
        **kwargs,
    ) -> Resource:
        """Create a dataset of type ``image``.

        One of ``company`` or ``project`` must be defined.

        Args:
            name: Name of the dataset.

            categories: Sequence of categories or None if there's no
                category to set on the dataset.

            company: Optional company identifier.

            project: Optional project identifier.

            mission: Optional mission identifier.

            flight: Optional flight identifier.

            hidden: Whether not to display the dataset to end-users or
                not.

            published: Whether the dataset is ready for delivery or
                not.

            horizontal_srs_wkt: Optional geographic coordinate system
                for horizontal coordinattes in WKT format.

            vertical_srs_wkt: Optional geographic coordinate system
                for vertical coordinattes in WKT format.

            dataset_format: Optional file format.

            geometry: Optional geometry of the dataset.

            properties: Optional custom properties of the dataset.

            acquisition_date: Optional acquisition date
                (format: ``YYYY-MM-DDTHH:MM:SS.sssZ``).

            width: Optional image width.

            height: Optional image height.

            sensor: Optional sensor properties.

            lens: Optional lens properties.

            camera_parameters: Optional camera parameters description.

            reflectance_calibration_panel: Optional reflectance calibration
                panel description.

            parse_metadata: Optional ingestion parameter that will populate dataset
                attributes with parsed Exif & XMP metadata

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: Resource for the created dataset.

        """
        params = kwargs

        if camera_parameters:
            params["camera_parameters"] = [camera_parameters]

        for k, v in [
            ("acquisition_date", acquisition_date),
            ("width", width),
            ("height", height),
            ("sensor", sensor),
            ("lens", lens),
            ("reflectance_calibration_panel", reflectance_calibration_panel),
        ]:
            if v:
                params.update({k: v})

        params.update(
            {
                "name": name,
                "categories": categories,
                "company": company,
                "project": project,
                "mission": mission,
                "flight": flight,
                "hidden": hidden,
                "published": published,
                "horizontal_srs_wkt": horizontal_srs_wkt,
                "vertical_srs_wkt": vertical_srs_wkt,
                "dataset_format": dataset_format,
                "geometry": geometry,
                "properties": properties,
            }
        )

        if parse_metadata is not None:
            dict_merge(
                params,
                {"ingestion": {"parameters": {"parse_metadata": parse_metadata}}},
            )

        components = ["image"]
        return self._create("image", components, **params)

    def create_raster_dataset(
        self,
        *,
        name: str,
        categories: Sequence[str] | None = None,
        company: ResourceId | None = None,
        project: ResourceId | None = None,
        mission: ResourceId | None = None,
        hidden: bool | None = None,
        published: bool | None = None,
        horizontal_srs_wkt: str | None = None,
        vertical_srs_wkt: str | None = None,
        dataset_format: str | None = None,
        geometry: dict | None = None,
        properties: dict | None = None,
        bands: List[dict] | None = None,
        has_projection_file: bool = False,
        has_worldfile: bool = False,
        has_headerfile: bool = False,
        **kwargs,
    ) -> Resource:
        """Create a dataset of type ``raster``.

        One of ``company`` or ``project`` must be defined.

        Args:
            name: Name of the dataset.

            categories: Sequence of categories or None if there's no
                category to set on the dataset.

            company: Optional company identifier.

            project: Optional project identifier.

            mission: Optional mission identifier.

            hidden: Whether not to display the dataset to end-users or
                not.

            published: Whether the dataset is ready for delivery or
                not.

            horizontal_srs_wkt: Optional geographic coordinate system
                for horizontal coordinattes in WKT format.

            vertical_srs_wkt: Optional geographic coordinate system
                for vertical coordinattes in WKT format.

            dataset_format: Optional file format.

            geometry: Optional geometry of the dataset.

            properties: Optional custom properties of the dataset.

            bands: Option list of band properties.

            has_projection_file: Whether there is a sidecar
                file to define the raster projection.

            has_worldfile: Whether there is a sidecar file to
                georeference the raster.

            has_headerfile: Whether there is a sidecar file for
                envi format raster.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: Resource for the created dataset.

        """
        params = kwargs

        if bands:
            params["bands"] = bands

        params.update(
            {
                "name": name,
                "categories": categories,
                "company": company,
                "project": project,
                "mission": mission,
                "hidden": hidden,
                "published": published,
                "horizontal_srs_wkt": horizontal_srs_wkt,
                "vertical_srs_wkt": vertical_srs_wkt,
                "dataset_format": dataset_format,
                "geometry": geometry,
                "properties": properties,
            }
        )

        components = ["raster"]
        if has_projection_file:
            components.append("projection")

        if has_worldfile:
            components.append("worldfile")

        if has_headerfile:
            components.append("header")

        return self._create("raster", components, **params)

    def create_pcl_dataset(
        self,
        *,
        name: str,
        categories: Sequence[str] | None = None,
        company: ResourceId | None = None,
        project: ResourceId | None = None,
        mission: ResourceId | None = None,
        hidden: bool | None = None,
        published: bool | None = None,
        horizontal_srs_wkt: str | None = None,
        vertical_srs_wkt: str | None = None,
        dataset_format: str | None = None,
        geometry: dict | None = None,
        properties: dict | None = None,
        **kwargs,
    ) -> Resource:
        """Create a dataset of type ``pcl``.

        One of ``company`` or ``project`` must be defined.

        Args:
            name: Name of the dataset.

            categories: Sequence of categories or None if there's no
                category to set on the dataset.

            company: Optional company identifier.

            project: Optional project identifier.

            mission: Optional mission identifier.

            hidden: Whether not to display the dataset to end-users or
                not.

            published: Whether the dataset is ready for delivery or
                not.

            horizontal_srs_wkt: Optional geographic coordinate system
                for horizontal coordinattes in WKT format.

            vertical_srs_wkt: Optional geographic coordinate system
                for vertical coordinattes in WKT format.

            dataset_format: Optional file format.

            geometry: Optional geometry of the dataset.

            properties: Optional custom properties of the dataset.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: Resource for the created dataset.

        """
        params = kwargs
        params.update(
            {
                "name": name,
                "categories": categories,
                "company": company,
                "project": project,
                "mission": mission,
                "hidden": hidden,
                "published": published,
                "horizontal_srs_wkt": horizontal_srs_wkt,
                "vertical_srs_wkt": vertical_srs_wkt,
                "dataset_format": dataset_format,
                "geometry": geometry,
                "properties": properties,
            }
        )
        components = ["pcl"]
        return self._create("pcl", components, **params)

    def create_vector_dataset(
        self,
        *,
        name: str,
        categories: Sequence[str] | None = None,
        company: ResourceId | None = None,
        project: ResourceId | None = None,
        mission: ResourceId | None = None,
        hidden: bool | None = None,
        published: bool | None = None,
        collection: ResourceId | None = None,
        origin: ResourceId | None = None,
        horizontal_srs_wkt: str | None = None,
        vertical_srs_wkt: str | None = None,
        dataset_format: str | None = None,
        geometry: dict | None = None,
        properties: dict | None = None,
        is_shape_file: bool = False,
        is_archive: bool = False,
        has_projection_file: bool = False,
        **kwargs,
    ) -> Resource:
        """Create a dataset of type ``vector``.

        When ``is_archive`` is True, ``is_shape_file`` and
        ``has_projection_file`` must be False.

        One of ``company`` or ``project`` must be defined.

        Args:
            name: Name of the dataset.

            categories: Sequence of categories or None if there's no
                category to set on the dataset.

            company: Optional company identifier.

            project: Optional project identifier.

            mission: Optional mission identifier.

            hidden: Whether not to display the dataset to end-users or
                not.

            published: Whether the dataset is ready for delivery or
                not.

            collection: Optional map-service collection to use as data
                source. Providing a collection isn't compatible with
                setting ``is_shape_file``, ``has_projection_file``,
                ``is_archive`` to True, nor setting ``dataset_format``.

            origin: Optional origin vector dataset (source: data-manager)
                for a vector collection dataset (source: map-service).

            horizontal_srs_wkt: Optional geographic coordinate system
                for horizontal coordinattes in WKT format.

            vertical_srs_wkt: Optional geographic coordinate system
                for vertical coordinattes in WKT format.

            dataset_format: Optional file format.

            geometry: Optional geometry of the dataset.

            properties: Optional custom properties of the dataset.

            is_shape_file: Whether it is an ESRI Shapefile.

            is_archive: Whether it is an archive.

            has_projection_file: Whether there is a sidecar
                file to define the shapes projection.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: Resource for the created dataset.

        """
        params = kwargs
        params.update(
            {
                "name": name,
                "categories": categories,
                "company": company,
                "project": project,
                "mission": mission,
                "hidden": hidden,
                "published": published,
                "horizontal_srs_wkt": horizontal_srs_wkt,
                "vertical_srs_wkt": vertical_srs_wkt,
                "dataset_format": dataset_format,
                "geometry": geometry,
                "properties": properties,
            }
        )

        components: Union[List[str], List[Dict[str, Any]]]

        if collection:
            component = {"name": "collection", "collection": {"id": collection}}
            if origin:
                component["origin"] = {"id": origin}
            components = [component]

            params["source"] = {"name": "map-service"}

            if any([is_shape_file, has_projection_file, is_archive, dataset_format]):
                raise ParameterError("Incompatible arguments")

        elif is_archive:
            components = ["archive"]

            if any([is_shape_file, has_projection_file]):
                raise ParameterError("Incompatible arguments")

        else:
            components = ["vector"]

            if is_shape_file:
                components += ["database", "index"]

            if has_projection_file:
                components += ["projection"]

        return self._create("vector", components, **params)

    @overload
    def describe(self, dataset: ResourceId, **kwargs) -> Resource: ...

    @overload
    def describe(self, dataset: List[ResourceId], **kwargs) -> List[Resource]: ...

    def describe(self, dataset: SomeResourceIds, **kwargs) -> SomeResources:
        """Describe a dataset or a list of datasets.

        Args:
            dataset: Identifier of the dataset to describe, or list of
                such identifiers.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            The dataset description or a list of dataset description.

        """
        data = kwargs
        if isinstance(dataset, list):
            results = []
            ids_chunks = get_chunks(dataset, self._provider.max_per_describe)
            for ids_chunk in ids_chunks:
                data["datasets"] = ids_chunk
                descs = self._provider.post("describe-datasets", data=data)
                results += [Resource(**desc) for desc in descs]
            return results
        else:
            data["dataset"] = dataset
            desc = self._provider.post("describe-dataset", data=data)
            return Resource(**desc)

    def delete(self, dataset: SomeResourceIds, **kwargs):
        """Delete a dataset or multiple datasets.

        Args:
            dataset: Identifier of the dataset to delete, or list of
                such identifiers.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs
        if not isinstance(dataset, list):
            dataset = [dataset]

        ids_chunks = get_chunks(dataset, self._provider.max_per_delete)
        for ids_chunk in ids_chunks:
            data["datasets"] = ids_chunk
            self._provider.post("delete-datasets", data=data, as_json=False)

    def restore(self, dataset: SomeResourceIds, **kwargs):
        """Restore a dataset or multiple datasets.

        Args:
            dataset: Identifier of the dataset to restore, or list of
                such identifiers.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs
        if not isinstance(dataset, list):
            dataset = [dataset]

        data["datasets"] = dataset
        self._provider.post("restore-datasets", data=data, as_json=False)

    def rename(self, dataset: ResourceId, *, name: str, **kwargs):
        """Rename the dataset.

        Args:
            dataset: Identifier of the dataset to rename.

            name: New name of the dataset.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs
        data.update({"dataset": dataset, "name": name})
        self._provider.post("rename-dataset", data=data)

    def update_properties(self, dataset: ResourceId, *, properties: dict, **kwargs):
        """Update the dataset properties.

        Args:
            dataset: Identifier of the dataset whose properties to
                update.

            properties: Dictionary of properties to update.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs
        data.update({"dataset": dataset, "properties": properties})
        self._provider.post("update-dataset-properties", data=data)

    def delete_properties(self, dataset: ResourceId, *, properties: List[str], **kwargs):
        """Delete properties of the dataset.

        Args:
            dataset: Identifier of the dataset whose properties to
                delete.

            properties: Names of properties to delete.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs
        data.update({"dataset": dataset, "properties": properties})
        self._provider.post("delete-dataset-properties", data=data)

    def add_categories(self, dataset: ResourceId, *, categories: List[str], **kwargs):
        """Add categories to the dataset.

        Args:
            dataset: Identifier of the dataset to add categories to.

            categories: Categories to add.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs
        data.update({"dataset": dataset, "categories": categories})
        self._provider.post("add-dataset-categories", data=data)

    def remove_categories(self, dataset: ResourceId, *, categories: List[str], **kwargs):
        """Remove categories from the dataset.

        Args:
            dataset: Identifier of the dataset to remove categories from.

            categories: Categories to remove.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs
        data.update({"dataset": dataset, "categories": categories})
        self._provider.post("delete-dataset-categories", data=data)

    def upload_file(
        self,
        dataset: ResourceId,
        *,
        component: str,
        file_path: AnyPath,
        md5hash: str | None = None,
        multipart: bool = True,
        chunk_size: int | None = None,
    ):
        """Upload a file to a dataset component.

        By default, it uploads directly into the storage provider, by using signed URIs.
        If you want to use the legacy upload method (not recommended), then change
        ``alteia.core.resources.datamngt.uploader.USE_LEGACY_UPLOADER`` to ``True``, or
        set env variable USE_LEGACY_UPLOADER=1 before running your script.

        Args:
            dataset: Identifier of the dataset to upload to.

            component: Name of component to upload to.

            file_path: Path to the file to upload.

            md5hash: Optional MD5 hash of the file to upload read in
                binary mode and containing only hexadecimal digits.
                Will be computed when equal to None (the default).

            multipart: Whether to upload the file using multipart
                upload. Default to ``True`` unless the total number of part is < 2.

            chunk_size: The size in byte of each part for a multipart upload.
                If file size is less than this number, multipart will not be used.
                The value is limited by storage provider and Data-Manager capabilities.
                5MiB is the min value.
        """

        du = DatasetUploader(self._provider, multipart, chunk_size)
        du.send(file_path, dataset=dataset, component=component, md5hash=md5hash)

    def _download(
        self,
        path: str,
        params: dict,
        target_path: Union[None, str],
        target_name: Union[None, str],
        overwrite: bool,
        md5hash: Optional[str],
    ) -> str:
        if target_path is None:
            target_path = "."

        if not os.path.exists(target_path):
            os.makedirs(target_path)

        url_path = f"{path}?{urllib.parse.urlencode(params)}"
        resp = self._provider.get(url_path, as_json=False, preload_content=False)
        file_name = target_name or extract_filename_from_headers(resp.headers)
        file_path = os.path.join(target_path, file_name)
        if not overwrite and os.path.exists(file_path):
            raise FileExistsError(f"File found at {file_path}")

        file_hash = hashlib.md5() if md5hash is not None else None
        with open(file_path, "wb") as fh:
            resp = self._stream_resp(resp, fh, file_hash=file_hash)

        if file_hash is not None and md5hash != file_hash.hexdigest():
            raise DownloadError("Unexpected MD5 hash")

        return file_path

    def _stream_resp(self, resp, dest, *, file_hash, offset=0):
        retries = resp.retries
        url = resp.geturl() or resp._request_url  # account for redirects
        method = "GET"
        err = None
        try:
            for chunk in resp.stream(4096):
                if chunk:  # false for keep-alive msg
                    dest.write(chunk)
                    offset += len(chunk)

                    if file_hash is not None:
                        file_hash.update(chunk)
        except (
            urllib3.exceptions.ReadTimeoutError,
            urllib3.exceptions.ProtocolError,
        ) as e:
            retries = retries.increment(method, url, error=e, _pool=resp._pool, _stacktrace=sys.exc_info()[2])
            retries.sleep()
            err = e
        finally:
            resp.release_conn()  # since not preload_content

        if err:
            headers = {"Cache-Control": "no-cache", "Range": f"bytes={offset}-"}
            # https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.35
            conn = self._provider._connection
            resp = conn.get(
                path=url,
                headers=headers,
                as_json=False,
                preload_content=False,
                retries=retries,
            )
            resp = self._stream_resp(resp, dest, file_hash=file_hash, offset=offset)
        return resp

    def download_component(
        self,
        dataset: ResourceId,
        *,
        component: str,
        target_path: str | None = None,
        target_name: str | None = None,
        overwrite=False,
        md5hash: str | None = None,
    ) -> str:
        """Download the file from a component.

        If the path ``target_path`` doesn't exists, it is created.

        Args:
            dataset: Identifier of the dataset to download from.

            component: Name of component to download from.

            target_path: Path of directory where to save the downloaded
                file. Default to current directory.

            target_name: Name of downloaded file. Default to the file
                name suggested by the server.

            overwrite: Whether to overwrite an existing file. Default
                to False.

            md5hash: Optional MD5 hash of the file to download read in
                binary mode and containing only hexadecimal digits.
                When not equal to ``None`` (the default), will be
                compared to the equivalent hash for the downloaded
                file.

        Raises:
            DownloadError: When the MD5 hash of the downloaded file
                doesn't match ``md5hash``.

        Returns:
            Path of the downloaded file.

        """
        params = {"dataset": dataset, "component": component}
        path = "download-component"
        return self._download(
            path,
            params=params,
            target_path=target_path,
            target_name=target_name,
            overwrite=overwrite,
            md5hash=md5hash,
        )

    def download_image_as_jpeg(
        self,
        dataset: ResourceId,
        target_path: str | None = None,
        target_name: str | None = None,
        overwrite=False,
        md5hash: str | None = None,
    ) -> str:
        """Download an image as JPEG.

        If the path ``target_path`` doesn't exists, it is created.

        Args:
            dataset: Identifier of the dataset to download from.

            target_path: Path of directory where to save the downloaded
                file. Default to current directory.

            target_name: Name of downloaded file. Default to the file
                name suggested by the server.

            overwrite: Whether to overwrite an existing file. Default
                to False.

            md5hash: Optional MD5 hash of the file to download read in
                binary mode and containing only hexadecimal digits.
                When not equal to ``None`` (the default), will be
                compared to the equivalent hash for the downloaded
                file.

        Raises:
            DownloadError: When the MD5 hash of the downloaded file
                doesn't match ``md5hash``.

        Returns:
            Path of the downloaded file.

        """
        params = {"dataset": dataset}
        path = "download-image-as-jpeg"
        return self._download(
            path,
            params=params,
            target_path=target_path,
            target_name=target_name,
            overwrite=overwrite,
            md5hash=md5hash,
        )

    def download_preview(
        self,
        dataset: ResourceId,
        kind: str | None = None,
        target_path: str | None = None,
        target_name: str | None = None,
        overwrite=False,
    ) -> str:
        """Download a dataset preview.

        If the path ``target_path`` doesn't exists, it is created.

        Args:
            dataset: Identifier of the dataset to download from.

            kind: Size of the preview, only for datasets type image.
                Must be `tiny` or `small`

            target_path: Path of directory where to save the downloaded
                file. Default to current directory.

            target_name: Name of downloaded file. Default to the file
                name suggested by the server.

            overwrite: Whether to overwrite an existing file. Default
                to False.

        Returns:
            Path of the downloaded file.

        """
        params = {"dataset": dataset}
        if kind is not None:
            params["kind"] = kind
        path = "download-preview"
        return self._download(
            path,
            params=params,
            target_path=target_path,
            target_name=target_name,
            overwrite=overwrite,
            md5hash=None,
        )

    def search(
        self,
        *,
        filter: dict | None = None,
        limit: int | None = None,
        page: int | None = None,
        sort: dict | None = None,
        return_total: bool = False,
        **kwargs,
    ) -> Union[ResourcesWithTotal, List[Resource]]:
        """Search datasets.

        Args:
            filter: Search filter dictionary (refer to ``/search-datasets``
                definition in the Data Manager API for a detailed description
                of ``filter``).

            limit: Optional Maximum number of results to extract.

            page: Optional Page number (starting at page 0).

            sort: Optional. Sort the results on the specified attributes
                (``1`` is sorting in ascending order,
                ``-1`` is sorting in descending order).

            return_total: Optional. Change the type of return:
                If ``False`` (default), the method will return a
                limited list of resources (limited by ``limit`` value).
                If ``True``, the method will return a namedtuple with the
                total number of all results, and the limited list of resources.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            A list of dataset descriptions OR a namedtuple
            with total number of results and list of dataset descriptions.

        Examples:
            >>> sdk.datasets.search(filter={'name': {'$eq': 'My image'}})
            [Resource(_id='5c5155ae8dcb064fcbf4ae35'), ...]

            >>> sdk.datasets.search(filter={'name': {'$eq': 'My image'}},
            ...                     return_total=True)
            ResourcesWithTotal(
                total=...,
                results=[Resource(_id='5c5155ae8dcb064fcbf4ae35'), ...]
            )

        """
        data = kwargs

        for name, value in [
            ("filter", filter or {}),
            ("limit", limit),
            ("page", page),
            ("sort", sort),
        ]:
            if value is not None:
                data.update({name: value})

        r = self._provider.post("search-datasets", data=data)

        datasets = r.get("results")

        results = [Resource(**dataset) for dataset in datasets]

        if return_total is True:
            total = r.get("total")
            return ResourcesWithTotal(total=total, results=results)
        else:
            return results

    def search_generator(
        self,
        *,
        filter: dict | None = None,
        limit: int = 50,
        page: int | None = None,
        count=False,
        **kwargs,
    ) -> Generator[Resource, None, None]:
        """Return a generator to search through datasets.

        The generator allows the user not to care about the pagination of
        results, while being memory-effective.

        Found datasets are sorted chronologically in order to allow
        new resources to be found during the search.

        Args:
            page: Optional page number to start the search at (default is 0).

            filter: Search filter dictionary.

            limit: Optional maximum number of results by search
                request (default to 50).

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            A generator yielding found datasets.

        """
        return search_generator(
            self,
            first_page=0,
            filter=filter,
            limit=limit,
            page=page,
            count=count,
            **kwargs,
        )

    def create_datasets(self, datasets: List[dict]) -> List[Resource]:
        """Create several datasets *(bulk dataset creation)*.

        Args:
            datasets: List of dataset dictionnaries
                (refer to ``/create-datasets``
                definition in the Data Manager API for a detailed description
                of ``datasets``)

        Returns:
            A list of the created dataset descriptions.

        Example:
            >>> sdk.datasets.create_datasets(
            ... datasets=[{'name': 'My file dataset',
            ...            'project': '4037636c9a406900074dc253',
            ...            'type': 'file',
            ...            'components': [{'name': 'kind_of_file'}]},
            ...           {'name': 'My image',
            ...            'type': 'image',
            ...            'project': '4037636c9a406900074dc253',
            ...            'components': [{'name': 'image'}]}])
            [Resource(_id='406ee155647ec6006df3aa21'), ...]

        """
        for desc in datasets:
            if "vertical_srs_wkt" in desc:
                desc["vertical_srs_wkt"] = expand_vertcrs_to_wkt(desc["vertical_srs_wkt"])

        data = {"datasets": datasets}
        created_datasets = self._provider.post("create-datasets", data=data)

        return [Resource(**dataset) for dataset in created_datasets]

    def share_tiles(self, dataset: SomeResourceIds, *, duration: int | None = None) -> str:
        """Return a URL template to share access to the tiles of the passed datasets.

        Args:
            dataset: Identifier of the dataset, or list of such identifiers
                (for rasters only) to create a URL for.

            duration: Optional duration in seconds of the created
                token. When equal to ``None`` (the default) the
                created token won't expire.

        Returns:
            url: The URL template of the shared tiles.

        Raises:
            UnsupportedResourceError: In case the dataset ingestion
               statuses aren't equal to ``complete`` or a dataset type isn't
               ``raster`` or ``vector`` with ``mapservice`` source, or dataset types
               are mixed.

        """
        if isinstance(dataset, list):
            dataset_ids = dataset
        else:
            dataset_ids = [dataset]

        datasets = self.describe(dataset_ids)

        if not isinstance(datasets, list):
            raise TypeError("Expecting a list of datasets")

        dataset_ids = [ds.id for ds in datasets]

        for ds_desc in datasets:
            ingested = hasattr(ds_desc, "ingestion") and ds_desc.ingestion.get("status", None) == "completed"
            if not ingested:
                raise UnsupportedResourceError(f"Ingestion not finished for dataset {ds_desc.id}")

        dataset_types = set(ds.type for ds in datasets)
        if len(dataset_types) > 1:
            raise UnsupportedResourceError(
                "Cannot mix dataset types when sharing tiles. " f'Provided: {", ".join(dataset_types)}'
            )

        elif dataset_types == {"vector"}:
            if len(datasets) != 1:
                raise UnsupportedResourceError("Cannot share more than 1 vector dataset")

            ds_desc = datasets[0]
            if ds_desc.source.get("name") != "map-service":
                raise UnsupportedResourceError('Cannot share a vector dataset. Expecting a source "map-service"')

            is_vector_in_mapservice = True

        elif dataset_types == {"raster"}:
            are_rasters = True

        else:
            raise UnsupportedResourceError(f'Unexpected dataset type: {", ".join(dataset_types)}.')

        if are_rasters and len(datasets) > MAX_RASTER_DATASETS_PER_TILE_URL:
            raise RuntimeError(
                f"Cannot share tiles for {len(datasets)} raster datasets. "
                f"Maximum allowed: {MAX_RASTER_DATASETS_PER_TILE_URL} datasets. "
                "Otherwise, the generated URL would be too long."
            )
        share_token = self._sdk.share_tokens.create(dataset=dataset_ids, duration=duration)
        base_url = self._provider._connection._base_url
        token = share_token.token

        if are_rasters:
            tile_formats = set([ds_desc.tiles.get("format", "png") for ds_desc in datasets])
            if len(tile_formats) != 1:
                raise UnsupportedResourceError("Dataset tile formats cannot be mixed")

            url = generate_raster_tiles_url(base_url, token, dataset_ids, ds_desc.tiles.get("format", "png"))
        elif is_vector_in_mapservice:
            collection_component_match = [
                c["collection"]["id"] for c in ds_desc.components if c.get("name") == "collection"
            ]
            if len(collection_component_match) != 1:
                raise UnsupportedResourceError("Unexpected number of components")

            collection_id = collection_component_match[0]
            url = generate_vector_tiles_url(base_url, token, collection_id, "pbf")

        if len(url) > MAX_URL_LENGTH:
            LOGGER.warning(
                f"The generated URL length is {len(url)} characters. "
                "You may encounter problems while using it on some clients. "
                f"Generally, try to keep a URL below {MAX_URL_LENGTH} characters. "
                "Try to reduce the number of datasets shared if needed."
            )

        return url
