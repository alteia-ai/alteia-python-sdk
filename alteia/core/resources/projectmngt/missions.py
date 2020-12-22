from alteia.core.resources.resource import Resource


class Mission(Resource):
    def __init__(self, **kwargs):
        """Mission resource.

        Args:
            id: Mission identifier.

            name: Mission name.

            project: Project identifier.

            survey_date: Survey date (format: ``YYYY-MM-DDTHH:MM:SS.sssZ``).

            flights: List of flight identifiers.

            geometry: Mission geometry.

            created: Mission creation date
                (format: ``YYYY-MM-DDTHH:MM:SS.sssZ``).

            user: Mission creation user.

            modification_date: Mission last modification date
                (format: ``YYYY-MM-DDTHH:MM:SS.sssZ``).

            modification_user: Mission last modification user.

            real_bbox: Mission bounding box.

        Returns:
            Mission: A mission resource.
        """
        super().__init__(**kwargs)
