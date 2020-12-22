"""Tag related resources.

"""

from alteia.core.resources.resource import Resource
from alteia.core.utils.typing import ResourceId


class Tag(Resource):
    def __init__(self, *, id: ResourceId, name: str, project: ResourceId,
                 type: str, creation_date: str, target: ResourceId = None,
                 flight: ResourceId = None, creation_user: ResourceId,
                 deletion_date: str = None, deletion_user: ResourceId = None,
                 **kwargs):
        """Tag resource.

        Args:
            id: Tag identifier.

            name: Tag name.

            project: Project identifier.

            type: Tag type (must be one of ``project``, ``annotation``,
                ``flight``, ``photo``, ``dataset``, ``feature``, ``gcp``,
                ``task``).

            target: Optional identifier of the target.

            flight: Optional identifier of the flight (mandatory when the tag
                type is ``photo``).

            creation_date: Tag creation date
                (format: ``YYYY-MM-DDTHH:MM:SS.sssZ``).

            creation_user: Tag creation user identifier.

            deletion_date: Optional deletion date
                (format: ``YYYY-MM-DDTHH:MM:SS.sssZ``).

            deletion_user: Optional deletion user.

            **kwargs: Optional keyword arguments. Those arguments are
                set as is in the ``Tag`` resource.

        Returns:
            Tag: A tag resource.
        """
        super().__init__(
            id=id,
            name=name,
            project=project,
            type=type,
            creation_date=creation_date,
            target=target,
            flight=flight,
            creation_user=creation_user,
            deletion_date=deletion_date,
            deletion_user=deletion_user,
            **kwargs
        )
