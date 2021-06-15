"""Implementation of annotations.

"""

import mimetypes
import os
from enum import Enum
from typing import AnyStr, Generator, List, Tuple, Union

from alteia.apis.provider import AnnotationsAPI
from alteia.core.errors import ParameterError
from alteia.core.resources.resource import Resource, ResourcesWithTotal
from alteia.core.resources.utils import search_generator
from alteia.core.utils.typing import (AnyPath, ResourceId, SomeResourceIds,
                                      SomeResources)

# TODO support for CSS3 colors


class AnnotationsImpl:
    class Icons(Enum):
        ANNOTATE = 'delair::icon::annotate'
        ARROW1 = 'delair::icon::arrow1'
        ARROW2 = 'delair::icon::arrow2'
        ARROW3 = 'delair::icon::arrow3'
        ARROW4 = 'delair::icon::arrow4'
        ARROW5 = 'delair::icon::arrow5'
        ARTICULATEDTRUCK = 'delair::icon::articulatedtruck'
        BULLDOZER = 'delair::icon::bulldozer'
        CANCEL = 'delair::icon::cancel'
        CHECK = 'delair::icon::check'
        COG = 'delair::icon::cog'
        COLLISION = 'delair::icon::collision'
        CONVEYOR = 'delair::icon::conveyor'
        CROSSROADS = 'delair::icon::crossroads'
        CROSSROADSUS = 'delair::icon::crossroadsUS'
        CRUSHER = 'delair::icon::crusher'
        DANGER = 'delair::icon::danger'
        DEF = 'delair::icon::def'
        DIESELFUEL = 'delair::icon::dieselfuel'
        DRAGLINE = 'delair::icon::dragline'
        DRILLS = 'delair::icon::drills'
        DROWNINGRISK = 'delair::icon::drowningrisk'
        DUMPER = 'delair::icon::dumper'
        DUMPTOPROCESS = 'delair::icon::dumptoprocess'
        DUSTHAZARD = 'delair::icon::dusthazard'
        DYNAMITE = 'delair::icon::dynamite'
        EARPROTECTION = 'delair::icon::earprotection'
        ELECTRICALRISK = 'delair::icon::electricalrisk'
        ELECTRICGENERATOR = 'delair::icon::electricgenerator'
        ENROCHMENTS = 'delair::icon::enrochments'
        EXCAVATOR = 'delair::icon::excavator'
        FALLFROMHEIGHTS = 'delair::icon::fallfromheights'
        FIREFIGHTERS = 'delair::icon::firefighters'
        FLAGGREEN = 'delair::icon::flaggreen'
        FLAGORANGE = 'delair::icon::flagorange'
        FLAGRED = 'delair::icon::flagred'
        FLOODRISK = 'delair::icon::floodrisk'
        FOG = 'delair::icon::fog'
        GLOVES = 'delair::icon::gloves'
        GRAVILLONS = 'delair::icon::gravillons'
        HOLE = 'delair::icon::hole'
        IMPACTCRUSHER = 'delair::icon::impactcrusher'
        INFORMATION = 'delair::icon::information'
        ISSUE = 'delair::icon::issue'
        LABSAMPLE = 'delair::icon::labsample'
        LIFEJACKET = 'delair::icon::lifejacket'
        MEETINGPOINT = 'delair::icon::meetingpoint'
        MOTORGRADER = 'delair::icon::motorgrader'
        NATURALSURROUNDINGS = 'delair::icon::naturalsurroundings'
        NOENTRY = 'delair::icon::noentry'
        NOISEMESURMENT = 'delair::icon::noisemesurment'
        ONEWAY = 'delair::icon::oneway'
        PARKING = 'delair::icon::parking'
        PERSONALPROTECTIVE = 'delair::icon::personalprotective'
        PRIORITY1 = 'delair::icon::priority1'
        PRIORITY10 = 'delair::icon::priority10'
        PRIORITY2 = 'delair::icon::priority2'
        PRIORITY3 = 'delair::icon::priority3'
        PRIORITY4 = 'delair::icon::priority4'
        PRIORITY5 = 'delair::icon::priority5'
        PRIORITY6 = 'delair::icon::priority6'
        PRIORITY7 = 'delair::icon::priority7'
        PRIORITY8 = 'delair::icon::priority8'
        PRIORITY9 = 'delair::icon::priority9'
        PRIORITYLEFT = 'delair::icon::priorityleft'
        PRIORITYRIGHT = 'delair::icon::priorityright'
        PROTECTIONMASK = 'delair::icon::protectionmask'
        RAILROADCROSSING = 'delair::icon::railroadcrossing'
        RAILS = 'delair::icon::rails'
        ROCKFALLS = 'delair::icon::rockfalls'
        ROUNDABOUT = 'delair::icon::roundabout'
        SABLE = 'delair::icon::sable'
        SAFETYGLASSES = 'delair::icon::safetyglasses'
        SCRAPER = 'delair::icon::scraper'
        SETTLINGPONT = 'delair::icon::settlingpont'
        SILO = 'delair::icon::silo'
        SISMOGRAPH = 'delair::icon::sismograph'
        SLIPPERY = 'delair::icon::slippery'
        SLOPE = 'delair::icon::slope'
        SLOPE2 = 'delair::icon::slope2'
        SPEEDLIMIT10 = 'delair::icon::speedlimit10'
        SPEEDLIMIT20 = 'delair::icon::speedlimit20'
        SPEEDLIMIT30 = 'delair::icon::speedlimit30'
        SPEEDLIMITUS10 = 'delair::icon::speedlimitUS10'
        SPEEDLIMITUS15 = 'delair::icon::speedlimitUS15'
        SPEEDLIMITUS20 = 'delair::icon::speedlimitUS20'
        STATIONERYCONE = 'delair::icon::stationerycone'
        STOCKPILE = 'delair::icon::stockpile'
        STOCKPILES = 'delair::icon::stockpiles'
        STOP = 'delair::icon::stop'
        TRAFFICACCIDENT = 'delair::icon::trafficaccident'
        TRAIN = 'delair::icon::train'
        TREES = 'delair::icon::trees'
        TURNLEFT = 'delair::icon::turnleft'
        TURNRIGHT = 'delair::icon::turnright'
        TWOWAYS = 'delair::icon::twoways'
        TWOWAYSPRIORITY = 'delair::icon::twowayspriority'
        VALVE = 'delair::icon::valve'
        WATER = 'delair::icon::water'
        WATERDISCHARGE = 'delair::icon::waterdischarge'
        WATERPUMP = 'delair::icon::waterpump'
        WATERTRUCK = 'delair::icon::watertruck'
        WHEELEDEXCAVATOR = 'delair::icon::wheeledexcavator'
        WIRES = 'delair::icon::wires'
        WRENCH = 'delair::icon::wrench'

    def __init__(self, annotations_api: AnnotationsAPI,
                 sdk, **kwargs):
        self._provider = annotations_api
        self._sdk = sdk

    def __upload_files(self, *, project: ResourceId,
                       file_paths: List[AnyPath]):
        datasets = []
        for p in file_paths:
            name = os.path.basename(p)
            file_type, _ = mimetypes.guess_type(p)
            file_subtype = file_type.split('/')[1] if file_type else None
            if file_subtype == 'image':
                creation_func = self._sdk.datasets.create_image_dataset
                component = 'image'
            else:
                creation_func = self._sdk.datasets.create_file_dataset
                component = 'file'

            dataset = creation_func(name=name, project=project)
            self._sdk.datasets.upload_file(dataset.id,
                                           component=component,
                                           file_path=p)
            datasets.append(dataset)
        return datasets

    def create(self, *, project: ResourceId,
               mission: ResourceId = None,
               geometry: dict = None,
               stroke: List[int] = None,
               stroke_dasharray: List[int] = None,
               icon: Union[Icons, str] = None,
               stroke_width: float = None,
               stroke_opacity: float = None,
               fill: List[int] = None,
               fill_opacity: float = None,
               type: AnyStr = '2d',
               target: ResourceId = None,
               name: AnyStr = None,
               description: AnyStr = None,
               followers: List[ResourceId] = None,
               attachments: List[ResourceId] = None,
               file_paths: List[AnyStr] = None,
               normals: List = None,
               **kwargs) -> Resource:
        """Create an annotation.

        Items of the ``file_paths`` argument are interpreted as file
        paths on the host file system. For each item, a dataset is
        created and the file at the given path is uploaded. The
        dataset will be attached to the created annotation.

        Refer to ``add_attachments()`` for details on the properties of
        the created datasets.

        Args:
            project: Identifier of project to annotate.

            mission: Identifier of mission to annotate.

            type: Annotation type (must be one of ``2d``, ``3d`` and
                ``image``).

            geometry: Geojson geometry of the annotation.

            stroke: Color used as annotation stroke list of integer
                    ``[r,g,b]`` or ``[r,g,b,a]``.

            stroke_dasharray: List of integer for dasharray display
                              (specify intervals of line and break).

            icon: Icon string or enum. Used for ``point`` annotations.
                Enum can be retrieved through ``sdk.annotations.Icons``
                (default: ``sdk.annotations.Icons.ANNOTATE``).

            stroke_width:  Width of stroke.

            stroke_opacity: Opacity of stroke between 0 and 1.

            fill: Color used as fill for annotation list of integer
                    [r,g,b] or [r,g,b,a]

            fill_opacity: Opacity of fill between 0 and 1.

            target: Identifier of the dataset to annotate.

            name: Annotation name.

            description: Annotation description.

            followers: Identifiers of users following the annotation.

            attachments: Identifiers of datasets to attach to the
                annotation.

            file_paths: List of file paths to upload and attach to the
                annotation.

            normals: Transformation vector used to transform the geometry on
                the front-end (for 3D datasets).

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: The created annotation.

        Examples:
            >>> sdk.annotations.create(
            ...    project='5d63cf9743d61400078efaf8',
            ...    geometry={
            ...        "type": "Point",
            ...        "coordinates": [1440.8495575221236, 1144.8259587020648]
            ...    },
            ...    name='My point annotation',
            ...    type='image',
            ...    target='5d63cf972fb3880011e57e34',
            ...    icon=sdk.annotations.Icons.CONVEYOR,
            ...    followers=['5d5fa52bc207040006390244'],
            ...    attachments=['5d63cf972fb3880011e57e32']
            ... )
            <alteia.core.resources.resource.Resource ... (annotations)>

        """
        if type not in ('2d', '3d', 'image'):
            raise ValueError('Unsupported type {}'.format(type))

        data = kwargs
        data.update({'project': project,
                     'type': type,
                     'geometry': geometry})

        if stroke is not None:
            data['stroke'] = stroke

        if stroke_dasharray is not None:
            data['stroke_dasharray'] = stroke_dasharray

        if icon is not None:
            if isinstance(icon, Enum):
                data['icon'] = icon.value
            else:
                data['icon'] = icon

        if stroke_width is not None:
            data['stroke_width'] = stroke_width

        if stroke_opacity is not None:
            data['stroke_opacity'] = stroke_opacity

        if fill is not None:
            data['fill'] = fill

        if fill_opacity is not None:
            data['fill_opacity'] = fill_opacity

        if mission is not None:
            data['mission'] = mission

        if target is not None:
            data['target'] = {'type': 'dataset', 'id': target}

        if name is not None:
            data['name'] = name

        if description is not None:
            data['description'] = description

        if followers is not None:
            data['followers'] = followers

        if attachments is not None:
            data['attachments'] = attachments

        if file_paths is not None:
            if attachments is None:
                attachments = []
            datasets = self.__upload_files(project=project,
                                           file_paths=file_paths)
            data['attachments'] += datasets

        if normals is not None:
            data['normals'] = normals

        desc = self._provider.post('create-annotation', data=data)
        return Resource(**desc)

    def create_annotations(self,
                           annotations: List[dict],
                           **kwargs) -> List[Resource]:
        """Create several annotations.

        Args:
            annotations: List of annotation descriptions, each
                description is a dictionary with keys among arguments of
                ``create()``.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Descriptions of the created annotations.

        """
        data = {'annotations': annotations}
        resp = self._provider.post('create-annotations', data=data)

        return [Resource(**desc)
                for desc in resp]

    def describe(self, annotation: SomeResourceIds, **kwargs) -> SomeResources:
        """Describe a dataset or a list of datasets.

        Args:
            annotation: Identifier of the annotation to describe, or list of
                such identifiers.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            The annotation description or a list of annotation description.

        """
        data = kwargs
        if isinstance(annotation, list):
            data['annotations'] = annotation
            descs = self._provider.post('describe-annotations', data=data)
            return [Resource(**desc)
                    for desc in descs]
        else:
            data['annotation'] = annotation
            desc = self._provider.post('describe-annotation', data=data)
            return Resource(**desc)

    def delete(self, annotation: SomeResourceIds, **kwargs):
        """Delete an annotation or multiple annotations.

        Args:
            annotation: Identifier of the annotation to delete, or
                list of such identifiers.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs
        if 'resource' in kwargs:
            raise RuntimeError('Support for "resource" parameter is not supported')

        if isinstance(annotation, Resource):
            raise RuntimeError('Support for parameters of type "Resource" is not supported')

        if not isinstance(annotation, list):
            annotation = [annotation]

        data['annotations'] = annotation
        self._provider.post('delete-annotations', data=data, as_json=False)

    def restore(self, annotation: SomeResourceIds, **kwargs):
        """Restore an annotation or multiple annotations.

        Args:
            annotation: Identifier of the annotation to restore, or list of
                such identifiers.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs
        if not isinstance(annotation, list):
            annotation = [annotation]

        data['annotations'] = annotation
        self._provider.post('restore-annotations', data=data, as_json=False)

    def rename(self, annotation: ResourceId, *, name: str, **kwargs):
        """Rename the annotation.

        Args:
            annotation: Identifier of the annotation to rename.

            name: New name of the annotation.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs
        data.update({'annotation': annotation,
                     'name': name})
        self._provider.post('rename-annotation', data=data)

    def set_description(self, annotation: ResourceId, *,
                        description: str, **kwargs):
        """Set the annotation description.

        Args:
            annotation: Identifier of the annotation whose description to set.

            description: Description of the annotation.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs
        data.update({'annotation': annotation,
                     'description': description})
        self._provider.post('set-annotation-description', data=data)

    def set_normals(self, annotation: ResourceId, *,
                    normals: List,
                    **kwargs):
        """Set the annotation normal vectors.

        Setting the normals of an annotation makes sense for
        annotations of type ``3d`` only. The argument ``normals`` is
        expected to be a list of 3-dimensional vectors, one for each
        vertice of the annotation geometry. Those vectors are
        interpreted as normals to the target of the annotation and are
        used to shift the annotation geometry when it is drawn so that
        it doesn't overlap the target of the annotation and is drawn
        on the right side of the target facets.

        Args:

            annotation: Identifier of the annotation whose normal
                vector to set.

            normals: List of coordinates of normal vectors.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs
        data.update({'annotation': annotation,
                     'normals': normals})
        self._provider.post('set-annotation-normals', data=data)

    def set_icon(self, annotation: ResourceId, *,
                 icon: Union[Icons, str] = None, **kwargs):
        """Set the annotation icon.

        Args:
            annotation: Identifier of the annotation whose icon to set.

            icon: Icon string or enum. Used for ``point`` annotations.
                Enum can be retrieved through ``sdk.annotations.Icons``
                (default: ``sdk.annotations.Icons.ANNOTATE``).

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs

        if isinstance(icon, Enum):
            icon = icon.value

        data.update({'annotation': annotation,
                     'icon': icon})
        self._provider.post('set-annotation-icon', data=data)

    def set_stroke_color(self, annotation: ResourceId, *,
                         color: Tuple[int, int, int],
                         opacity: float = None,
                         **kwargs):
        """Set the stroke color of the annotation.

        Args:
            annotation: Identifier of the annotation whose stroke color to set.

            color: Stroke color to set interpreted as an RGB-triple.

            opacity: Optional opacity of stroke color, a float number between 0
                and 1.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs
        stroke = list(color)
        if opacity is not None:
            stroke.append(opacity)

        data.update({'annotation': annotation,
                     'stroke': stroke})
        self._provider.post('set-annotation-stroke', data=data)

    def set_stroke_width(self, annotation: ResourceId, *,
                         width: float, **kwargs):
        """Set the stroke width of the annotation.

        Args:
            annotation: Identifier of the annotation whose stroke width to set.

            width: Stroke width to set.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs
        data.update({'annotation': annotation,
                     'stroke_width': width})
        self._provider.post('set-annotation-stroke-width', data=data)

    def set_stroke_opacity(self, annotation: ResourceId, *,
                           opacity: float, **kwargs):
        """Set the opacity of the annotation stroke.

        Args:
            annotation: Identifier of the annotation whose stroke opacity to
                set.

            opacity: Stroke opacity to set.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs
        data.update({'annotation': annotation,
                     'stroke_opacity': opacity})
        self._provider.post('set-annotation-stroke-opacity', data=data)

    def set_stroke_dasharray(self, annotation: ResourceId, *,
                             dasharray: List[float], **kwargs):
        """Set the dasharray of the annotation stroke.

        The dasharray defines the pattern of dashes and gaps used to
        paint the outline of the annotation.

        Args:
            annotation: Identifier of the annotation whose stroke opacity to
                set.

            dasharray: Dasharray to set.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs
        data.update({'annotation': annotation,
                     'stroke_dasharray': dasharray})
        self._provider.post('set-annotation-stroke-dasharray', data=data)

    def set_fill_color(self, annotation: ResourceId, *,
                       color: List[float], opacity: float = None,
                       **kwargs):
        """Set the color used to fill the annotation.

        Args:
            annotation: Identifier of the annotation whose fill color to
                set.

            color: Fill color to set interpreted as an RGB-triple.

            opacity: Optional opacity of fill color, a float number between 0
                and 1.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs
        fill = list(color)
        if opacity is not None:
            fill.append(opacity)

        data.update({'annotation': annotation,
                     'fill': fill})
        self._provider.post('set-annotation-fill', data=data)

    def set_fill_opacity(self, annotation: ResourceId, *,
                         opacity: float, **kwargs):
        """Set the opacity of the annotation fill.

        Args:
            annotation: Identifier of the annotation whose fill opacity to
                set.

            opacity: Fill opacity to set.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs
        data.update({'annotation': annotation,
                     'fill_opacity': opacity})
        self._provider.post('set-annotation-fill-opacity', data=data)

    def set_geometry(self, annotation: ResourceId, *,
                     geometry: dict, **kwargs):
        """Set the geometry of the annotation.

        Args:
            annotation: Identifier of the annotation whose geometry to
                set.

            geometry: A dictionary following GeoJSON specification.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs
        data.update({'annotation': annotation,
                     'geometry': geometry})
        self._provider.post('set-annotation-geometry', data=data)

    def add_attachments(self, annotation: ResourceId, *,
                        attachments: List[ResourceId] = None,
                        file_paths: List[AnyStr] = None,
                        **kwargs):
        """Attach datasets to the annotation.

        An attachment is a reference to a dataset handled by the Data
        Management API.

        Items of the ``file_paths`` argument are interpreted as file
        paths on the host file system. For each item, a dataset is
        created and the file at the given path is uploaded. The
        dataset will be attached to the created annotation.

        The created dataset has the following properties:

        - It's type is equal to ``file`` or ``image`` depending on the
          local file MIME type.

        - It belongs to the same project as the annotation.

        - It's named is equal to the basename of the local file.

        For fine control of the dataset type, mission, published
        status, etc. or when the dataset has multiple components, one
        must create the dataset separately and use the ``attachment``
        argument.

        Args:
            annotation: Identifier of the annotation to attach to.

            attachments: Identifiers of dataset to attach to the
                annotation.

            file_paths: List of file path to upload and attach to the
                annotation.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs

        if attachments is None and file_paths is None:
            raise ParameterError('One of {!r} or {!r} must be specified'
                                 .format('attachments', 'file_paths'))

        if file_paths is not None:
            if attachments is None:
                attachments = []

            a = self.describe(annotation)
            datasets = self.__upload_files(project=a.project,
                                           file_paths=file_paths)
            attachments += datasets

        data.update({'annotation': annotation,
                     'attachments': attachments})
        self._provider.post('add-attachments', data=data)

    def remove_attachments(self, annotation: ResourceId, *,
                           attachments: SomeResourceIds,
                           **kwargs):
        """Remove attachment to the annotation.

        Args:
            annotation: Identifier of the annotation to remove attachments
                 from.

            attachments: Identifier of attachments to remove.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs

        data.update({'annotation': annotation,
                     'attachments': attachments})
        self._provider.post('remove-attachments', data=data)

    def search_generator(self, *, filter: dict = None, limit: int = 50,
                         page: int = None,
                         **kwargs) -> Generator[Resource, None, None]:
        """Return a generator to search through annotations.

        The generator allows the user not to care about the pagination of
        results, while being memory-effective.

        Found annotations are sorted chronologically in order to allow
        new resources to be found during the search.

        Args:
            page: Optional page number to start the search at (default is 0).

            filter: Search filter dictionary.

            limit: Optional maximum number of results by search
                request.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            A generator yielding found annotations.

        """
        return search_generator(self, first_page=1, filter=filter, limit=limit,
                                page=page, **kwargs)

    def search(self, *, project: ResourceId = None, filter: dict = None,
               limit: int = None, page: int = None, sort: dict = None,
               return_total: bool = False,
               **kwargs) -> Union[ResourcesWithTotal, List[Resource]]:
        """Search annotations.

        Args:
            project: Optional identifier of a project to search
                annotatons for.

            filter: Search filter dictionary (refer to ``/search-annotations``
                in the Annotation API specification for a detailed
                description).

            limit: Maximum number of results.

            page: Page number (starting at page 0).

            sort: Sort the results on the specified attributes
                (``1`` is sorting in ascending order,
                ``-1`` is sorting in descending order).

            return_total: Return the number of results found.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            A list of annotation descriptions or a namedtuple
            with total number of results and list of annotation descriptions.

        """
        data = kwargs
        for name, value in [('filter', filter or {}),
                            ('limit', limit),
                            ('page', page),
                            ('sort', sort)]:
            if value is not None:
                data.update({name: value})

        if project is not None:
            data['filter'].update({'project': {'$eq': project}})

        r = self._provider.post('search-annotations', data=data)

        annotations = r.get('results')
        results = [Resource(**a) for a in annotations]

        if return_total is True:
            total = r.get('total')
            return ResourcesWithTotal(total=total, results=results)
        else:
            return results
