"""Comment related resources.

"""

from alteia.core.resources.resource import Resource
from alteia.core.utils.typing import ResourceId


class Comment(Resource):
    def __init__(self, *, id: ResourceId, text: str, project: ResourceId,
                 type: str, creation_date: str, target: ResourceId = None,
                 flight: ResourceId = None, creation_user: ResourceId,
                 deletion_date: str = None, deletion_user: ResourceId = None,
                 **kwargs):
        """Comment resource.

        Args:
            id: Comment identifier.

            text: Comment content.

            project: Project identifier.

            type: Comment type (must be one of ``project``, ``annotation``,
                ``flight``, ``photo``, ``dataset``, ``feature``, ``gcp``,
                ``task``).

            target: Optional identifier of the target.

            flight: Optional identifier of the flight (mandatory when the
                comment type is ``photo``).

            creation_date: Comment creation date
                (format: ``YYYY-MM-DDTHH:MM:SS.sssZ``).

            creation_user: Comment creation user identifier.

            **kwargs: Optional keyword arguments. Those arguments are
                set as is in the ``Comment`` resource.

        Returns:
            Comment: A comment resource.
        """
        super().__init__(
            id=id,
            text=text,
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
