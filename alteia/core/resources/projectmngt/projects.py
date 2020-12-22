from alteia.core.resources.resource import Resource


class Project(Resource):
    def __init__(self, **kwargs):
        """Project resource.

        Args:
            id: Project identifier.

            name: Project name.

            geometry: Project geometry.

            industry: Project industry.

            created: Project creation date
                (format: ``YYYY-MM-DDTHH:MM:SS.sssZ``).

            company: Project's company identifier.

            missions: Project's mission identifiers.

            user: Project creation user.

            modification_date: Project last modification date
                (format: ``YYYY-MM-DDTHH:MM:SS.sssZ``).

            modification_user: Project last modification user.

            real_bbox: Project bounding box.

            place_name: Project place name.

        Returns:
            Project: A project resource.
        """
        # Rename companyId key to company in order to have consistent naming
        if kwargs.get('companyId'):
            kwargs['company'] = kwargs.pop('companyId')
        super().__init__(**kwargs)
