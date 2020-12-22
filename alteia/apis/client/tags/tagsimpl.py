"""Implementation of tags.

"""

import urllib.parse
from typing import List

from alteia.apis.provider import UIServicesAPI
from alteia.core.errors import ParameterError
from alteia.core.resources.tags import Tag
from alteia.core.utils.typing import ResourceId


class TagsImpl:
    def __init__(self, ui_services_api: UIServicesAPI,
                 sdk, **kwargs):
        self._provider = ui_services_api
        self._sdk = sdk

    def create(self, name: str, *, project: ResourceId,
               type: str, target: ResourceId = None, flight: ResourceId = None,
               **kwargs) -> Tag:
        """Create a tag.

        Args:
            name: Tag name.

            project: Identifier of project to tag.

            type: Tag type (must be one of ``project``, ``annotation``,
                ``flight``, ``photo``, ``dataset``, ``feature``, ``gcp``,
                ``task``).

            target: Optional identifier of the target.

            flight: Optional identifier of the flight (mandatory when the tag
                type is ``photo``).

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Tag: The created tag.

        Examples:
            >>> sdk.tags.create(
            ...    name='my tag',
            ...    project='5d63cf972fb3880011e57f22',
            ...    type='dataset',
            ...    target='5d63cf972fb3880011e57e34')
            <alteia.core.resources.tags.Tag with id ... (tags)>

        """
        data = kwargs
        data.update({'project_id': project,
                     'text': name,
                     'target': {'type': type}})

        if type == 'photo':
            if target is None or flight is None:
                raise ParameterError('When tagging a photo, '
                                     'the target and flight must be defined')
            else:
                data['target']['id'] = flight
                data['target']['subId'] = target

        elif target is not None:
            data['target']['id'] = target

        res = self._provider.post('tags', data=data)
        return self._convert_uisrv_desc_to_Tag(res['tag'])

    def _convert_uisrv_desc_to_Tag(self, desc: dict) -> Tag:
        """Convert a tag description returned by UI-Services to a Tag object"""
        # {'Tag_key': 'uisrv_desc_key'}
        params = {}

        name = desc.pop('text')
        project = desc.pop('project_id')
        creation_date = desc.pop('date')
        type = desc['target'].pop('type')
        creation_user = desc['author'].pop('id')

        if desc.get('deleted') is not None:
            params['deletion_date'] = desc.pop('deleted')
        if desc['target'].get('subId'):
            params['target'] = desc['target'].pop('subId')
            params['flight'] = desc['target'].pop('id')
        elif desc['target'].get('id'):
            params['target'] = desc['target'].pop('id')
        desc.pop('target')

        desc.pop('author')

        if desc.get('deleted_by'):
            params['deletion_user'] = desc['deleted_by'].pop('id')
            desc.pop('deleted_by')

        params.update(desc)  # Save remaining properties (should be empty)

        return Tag(
            id=desc['_id'],
            name=name,
            project=project,
            creation_date=creation_date,
            type=type,
            creation_user=creation_user,
            **params
        )

    def search(self, *, project: ResourceId, type: str = None,
               target: ResourceId = None, flight: ResourceId = None,
               **kwargs) -> List[Tag]:
        """Search tags.

        When searching for tags on a photo. Both the ``flight`` id and
        ``target`` id must be supplied.

        Args:
            project: Identifier of the project.

            type: Optional tag type (must be one of ``project``,
                ``annotation``, ``flight``, ``photo``, ``dataset``,
                ``feature``, ``gcp``, ``task``).

            target: Optional identifier of the target.

            flight: Optional identifier of the flight (mandatory when the tag
                type is ``photo``).

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resources: The found tags.

        Examples:
            >>> sdk.tags.search(project='5d63cf972fb3880011e57f22')
            [<alteia.core.resources.tags.Tag with id ... (tags)>]

        """
        query = kwargs
        query['project_id'] = project

        if type:
            query['target_type'] = type

        if flight:
            query['target_id'] = flight
            if target:
                # the target is a photo id when a flight id is supplied
                query['target_subid'] = target

        elif target:
            query['target_id'] = target

        query_str = urllib.parse.urlencode(query)
        path = 'tags?{}'.format(query_str)

        desc = self._provider.get(path)

        found_tags = []
        for group in desc.get('tagGroups'):
            for tag in group.get('tags'):
                tag.update({'project_id': project})
                tag.update({'target': group.get('_id').copy()})
                found_tags.append(self._convert_uisrv_desc_to_Tag(desc=tag))
        return found_tags

    def delete(self, tag: ResourceId) -> None:
        """Delete a tag.

        Args:
            tag: Identifier of the tag to delete.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Examples:
            >>> sdk.tags.delete('5d63cf972fb3880011e57f22')

        """

        self._provider.delete('tags/{}'.format(tag))
