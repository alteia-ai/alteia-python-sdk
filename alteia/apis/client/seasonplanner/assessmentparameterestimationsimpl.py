from typing import List, Union

from alteia.apis.provider import SeasonPlannerAPI
from alteia.core.resources.resource import Resource, ResourcesWithTotal
from alteia.core.resources.utils import search
from alteia.core.utils.typing import ResourceId


class AssessmentParameterEstimationsImpl:
    def __init__(self, season_planner_api: SeasonPlannerAPI, **kwargs):
        self._provider = season_planner_api

    def search(self, *, filter: dict = None, limit: int = None, fields: dict = None,
               page: int = None, sort: dict = None, return_total: bool = False,
               **kwargs) -> Union[ResourcesWithTotal, List[Resource]]:
        """Search assessment-parameter-estimations.

        Args:
            filter: Search filter dictionary.
                    ``{
                        "_id": {
                            "$eq": "string"
                        },
                        "company": {
                            "$eq": "string"
                        },
                        "creation_date": {
                            "$eq": "2019-08-24T14:15:22Z"
                        },
                        "modification_date": {
                            "$eq": "2019-08-24T14:15:22Z"
                        },
                        "deletion_date": {
                            "$eq": "2019-08-24T14:15:22Z"
                        },
                        "trial": {
                            "$eq": "string"
                        },
                        "mission": {
                            "$eq": "string"
                        },
                        "estimation_method": {
                            "$eq": "string"
                        },
                        "collection_task": {
                            "$eq": "string"
                        },
                        "survey": {
                            "$eq": "string"
                        },
                        "product": {
                            "$eq": "string"
                        },
                        "status": {
                            "$in": [
                                "pending"
                            ]
                        }
                    }``

            limit: Maximum number of results to extract. Default: 1000.

            page: Page number (starting at page 0).

            fields: Optional properties to include or exclude from the response.
                ``{"include: ["name", "creation_date"]}``
                ``{"exclude: ["name", "creation_date"]}``
                Do not use both `include` and `exclude`.

            sort: Sort the results on the specified attributes
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
            Resources: A list of resources OR a namedtuple
                with total number of results and list of resources.

        """
        return search(
            self,
            url='search-assessment-parameter-estimations',
            filter=filter,
            fields=fields,
            limit=limit,
            page=page,
            sort=sort,
            return_total=return_total,
            **kwargs
        )

    def start_analysis_on_ape(self, assessment_parameter_estimation: ResourceId,
                              **kwargs) -> Resource:
        """Start analysis on APE.

        Args:
            assessment_parameter_estimation: Identifier of the assessment-parameter-estimation.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: A assessment-parameter-estimation resource.
        """
        data = kwargs
        data['assessment_parameter_estimation'] = assessment_parameter_estimation

        content = self._provider.post(
            path='start-analysis-on-ape',
            data=data
        )

        return Resource(**content)

    def start_reporting_on_ape(self, assessment_parameter_estimation: ResourceId,
                               **kwargs) -> Resource:
        """Start reporting on APE.

        Args:
            assessment_parameter_estimation: Identifier of the assessment-parameter-estimation.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Resource: A assessment-parameter-estimation resource.
        """
        data = kwargs
        data['assessment_parameter_estimation'] = assessment_parameter_estimation

        content = self._provider.post(
            path='start-reporting-on-ape',
            data=data
        )

        return Resource(**content)

    def export_report_entries(self, filter: dict, **kwargs):
        """Export report entries.

        Args:
            filter: Search filter dictionary.
                ``{
                    "_id": {
                        "$eq": "123456789abcdef012345678"
                    },
                    "trial": {
                        "$eq": "123456789abcdef012345678"
                    },
                    "mission": {
                        "$eq": "5f02f308a6f7f53d73962efc"
                    },
                    "ap_estimation": {
                        "$eq": "5f9ab771ce4e163c170bfe72"
                    },
                    "creation_date": {
                        "$eq": "2019-08-24T14:15:22Z"
                    }
                }``

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        """
        data = kwargs

        for name, value in [('filter', filter or {})]:
            if value is not None:
                data.update({name: value})

        r = self._provider.post(
            path='export-report-entries',
            data=data
        )
        results = r.get('results')

        return results
