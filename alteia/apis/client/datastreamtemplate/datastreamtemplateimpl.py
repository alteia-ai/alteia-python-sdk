from typing import Dict, List, Union

from alteia.apis.provider import DataflowServiceAPI
from alteia.core.resources.resource import ResourcesWithTotal
from alteia.core.utils.typing import Resource, ResourceId


class DatastreamTemplateImpl:
    def __init__(self, dataflow_service_api: DataflowServiceAPI, **kwargs):
        self._provider = dataflow_service_api

    def create(
        self,
        *,
        name: str,
        source: Dict,
        import_dataset: Dict,
        **kwargs
    ) -> Resource:
        """Create a datastream template.

        Args:
            name: Datastream template name.

            source: Storage source.

            import_dataset: dataset parameter, information for the creating of dataset.

                type: dataset type(pcl, file, image, raster, maesh, vector)

                categories: Sequence of categories or None if there's no
                    category to set on the dataset.

                horizontal_srs_wkt: Optional geographic coordinate system
                    for horizontal coordinattes in WKT format.

                ingestion: ingestion parameters

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            The created datastream template description.

        Examples:
            >>> sdk.datastreamtemplates.create(
            ...     name="My datastream template",
            ...     source= {"type":"object-storage"},
            ...     import_dataset= {"dataset_parameters":
            ...         {
            ...             "type": "pcl",
            ...             "categories": [],
            ...             "horizontal_srs_wkt": 'PROJCS["WGS 84 / UTM zone 31N",GEOGCS["WGS 84",
            ...                                           DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,
            ...                                           AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],
            ...                                           PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],
            ...                                           UNIT["degree",0.0174532925199433,
            ...                                           AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],
            ...                                           PROJECTION["Transverse_Mercator"],
            ...                                           PARAMETER["latitude_of_origin",0],
            ...                                           PARAMETER["central_meridian",3],
            ...                                           PARAMETER["scale_factor",0.9996],
            ...                                           PARAMETER["false_easting",500000],
            ...                                           PARAMETER["false_northing",0],
            ...                                           UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],
            ...                                           AXIS["Northing",NORTH],AUTHORITY["EPSG","32631"]]',
            ...             "ingestion": {"parameters": {"compute_boundary": True}},
            ...         }
            ...     },
            ...     contextualisation= {
            ...         "type": "geographic",
            ...         "parameters": {
            ...             "assets_schema_repository": "My Asset Repository",
            ...             "geographic_buffer": 50,
            ...             "schemas": [
            ...                 {
            ...                     "assets_schema": "My_asset",
            ...                     "assets_schema_property_name": "My asset property,
            ...                     "geographic_buffer": 150,
            ...                 }
            ...             ],
            ...         },
            ...     },
            ...     transform= {
            ...         "analytic": {
            ...             "name": "datastream",
            ...             "version_range": "XXX YYY",
            ...             "inputs_mapping": {},
            ...             "parameters": {},
            ...             "outputs_mapping": "",
            ...         },
            ...      },
            ...     "aggregate": {"type": "", "parameters": {}, "strategy": {}},
            ...     "company": "XXX"
            ...     "description": "My datastream description",
            ... )
            Resource(_id='5e5155ae8dcb064fcbf4ae35')

        """
        data: Dict = kwargs
        template = {
            "name": name,
            "source": source,
            "import": import_dataset,
        }

        data.update(template)

        desc = self._provider.post(path="create-datastream-template", data=data)

        return Resource(**desc)

    def delete(self, template: ResourceId) -> None:
        """Delete a datastream template entry.

        Args:
            template: datastream template identifier.

        """

        data: Dict = dict(datastreamtemplate=template)

        self._provider.post(path="delete-datastream-template", data=data, as_json=False)

    def search(
        self,
        *,
        filter: Dict = None,
        limit: int = None,
        page: int = None,
        sort: dict = None,
        exclude: List[str] = None,
        return_total: bool = False,
        **kwargs
    ) -> Union[ResourcesWithTotal, List[Resource]]:
        """Search for a list of datastream templates.

        Args:
            company: Company id.

            filter: Search filter dictionary (refer to ``/search-datastream-templates``
                definition in the Datastream Service API for a detailed
                description of ``filter``).

            limit: Optional Maximum number of results to extract.

            page: Optional Page number (starting at page 0).

            sort: Optional Sort the results on the specified attributes
                (``1`` is sorting in ascending order,
                ``-1`` is sorting in descending order).

            exclude: The properties to exclude from the response

            return_total: Optional. Change the type of return:
                If ``False`` (default), the method will return a
                limited list of resources (limited by ``limit`` value).
                If ``True``, the method will return a namedtuple with the
                total number of all results, and the limited list of resources.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            A list of datastream template resources OR a namedtuple
                with total number of results and list of datastream template resources.

        """
        data = kwargs

        for prop_name, value in [
            ("filter", filter or {}),
            ("limit", limit),
            ("page", page),
            ("sort", sort),
            ("exlude", exclude),
        ]:
            if value is not None:
                data.update({prop_name: value})

        desc = self._provider.post(path="search-datastream-templates", data=data)

        datastream = desc.get("results")

        results = [Resource(**data) for data in datastream]

        if return_total:
            total = desc.get("total")
            return ResourcesWithTotal(total=total, results=results)

        return results

    def describe(self, *, template: ResourceId) -> Resource:
        """Describe a datastream template.

        Args:
            templates: Identifier of the datastream template to describe.

        Returns:
            The datastream template description.

        """

        data: Dict = dict(datastreamtemplate=template)

        desc = self._provider.post(path="describe-datastream-template", data=data)

        return Resource(**desc)

    def describes(self, *, templates: List[ResourceId]) -> List[Resource]:
        """Describe datastream templates.

        Args:
            templates: List of such identifiers.

        Returns:
           A list of datastream template description.

        """

        data: Dict = dict(datastreamtemplates=templates)

        desc = self._provider.post(path="describe-datastream-templates", data=data)

        return [Resource(**data) for data in desc]
