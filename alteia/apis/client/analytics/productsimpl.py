"""Products implementation
"""

import time
from datetime import datetime, timedelta
from typing import Dict, Generator, List, Union

from alteia.apis.provider import AnalyticsServiceAPI
from alteia.core.resources.analytics.products import (ProductLog,
                                                      ProductLogsWithTotal)
from alteia.core.resources.resource import Resource, ResourcesWithTotal
from alteia.core.resources.utils import search_generator
from alteia.core.utils.typing import ResourceId


class ProductsImpl:
    def __init__(self, analytics_service_api: AnalyticsServiceAPI, **kwargs):
        self._provider = analytics_service_api

    def search(self, *, project: ResourceId = None, filter: Dict = None,
               limit: int = None, page: int = None, sort: dict = None,
               return_total: bool = False,
               **kwargs) -> Union[ResourcesWithTotal, List[Resource]]:
        """Search for Analytics products.

        Args:
            project: Project identifier.

            filter: Search filter dictionary (refer to ``/search-products``
                definition in the Analytics-service API for a detailed description
                of ``filter``).

            limit: Maximum number of results to extract.

            page: Page number (starting at page 0).

            sort: Sort the results on the specified attributes
                (``1`` is sorting in ascending order,
                ``-1`` is sorting in descending order).

            return_total: Return the number of results found.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Products: A list of product resources OR a namedtuple
                with total number of results and list of product resources.

        """
        data = kwargs

        for name, value in [('filter', filter or {}),
                            ('limit', limit),
                            ('page', page),
                            ('sort', sort)]:
            if value is not None:
                data.update({name: value})

        if project is not None:
            data['filter']['project'] = {"$eq": project}

        search_desc = self._provider.post(
            path='search-products', data=data, as_json=True)

        products = search_desc.get('results')

        results = [Resource(**product) for product in products]

        if return_total is True:
            total = search_desc.get('total')
            return ResourcesWithTotal(total=total, results=results)
        else:
            return results

    def search_generator(self, *, filter: dict = None, limit: int = 50,
                         page: int = None,
                         **kwargs) -> Generator[Resource, None, None]:
        """Return a generator to search through products.

        The generator allows the user not to care about the pagination of
        results, while being memory-effective.

        Found products are sorted chronologically in order to allow
        new resources to be found during the search.

        Args:
            page: Optional page number to start the search at (default is 0).

            filter: Search filter dictionary.

            limit: Optional maximum number of results by search
                request (default to 50).

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            A generator yielding found products.

        """
        return search_generator(self, first_page=0, filter=filter, limit=limit,
                                page=page, **kwargs)

    def describe(self, product: ResourceId, **kwargs) -> Resource:
        """Describe an Analytics product.

        Args:
            product: Identifier of the product to describe.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            The product description.

        Raises:
            ResponseError: When the ``product`` identifier is incorrect or has
                not been found.

        """
        data = kwargs

        data['product'] = product
        desc = self._provider.post('describe-product', data=data)
        return Resource(**desc)

    def cancel(self, product: ResourceId) -> Resource:
        """Cancel a running Analytics product.

        Args:
            product: Identifier of the product to cancel.

        Returns:
            The product description.

        Raises:
            ResponseError: When the ``product`` identifier is incorrect or has
                not been found.

        """
        data = {'product': product}
        desc = self._provider.post('cancel-product', data=data)
        return Resource(**desc)

    def retrieve_logs(self, product: ResourceId,
                      **kwargs) -> ProductLogsWithTotal:
        """Retrieve logs for a product (sorted chronogically).

        Args:
            product: Identifier of the product.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            Logs: A namedtuple with total number of log entries
                and the list of product logs.
        """
        data = kwargs
        data['product'] = product
        desc = self._provider.post('retrieve-product-logs', data=data)
        logs = []
        raw_logs = desc.get('logs')
        for raw_log in sorted(raw_logs, key=lambda log: log.get('timestamp')):
            timestamp_str = raw_log.get('timestamp')
            # Ex: '2020-04-16T08:35:42.338000000+00:00'
            # Truncate before Z chars to keep up to milliseconds
            z_index = timestamp_str.rfind('Z')
            clip_index = min(z_index, 26)
            d = datetime.strptime(timestamp_str[:clip_index], '%Y-%m-%dT%H:%M:%S.%f')
            logs.append(ProductLog(timestamp=d, record=raw_log))

        return ProductLogsWithTotal(
            total=desc.get('total').get('value'), logs=logs
        )

    def follow_logs(self, product: ResourceId,
                    **kwargs) -> Generator[ProductLog, None, None]:
        """Follow logs for a product through a generator.

        The function returns when the product status is either ``available``,
            ``failed`` or ``rejected``.

        Args:
            product: Identifier of the product.

            **kwargs: Optional keyword arguments. Those arguments are
                passed as is to the API provider.

        Returns:
            A generator yielding each log entry chronologically.
        """
        FINAL_STATES = ('available', 'failed', 'rejected')
        WAIT_BETWEEN_CALLS = 2  # seconds
        WAIT_AFTER_FINAL_STATE = 10  # seconds

        finished = False
        last_entry_date = None
        final_state_date = None  # When we encounter the final status

        while not finished:
            product_desc = self.describe(product)

            if product_desc.status in FINAL_STATES:
                if not final_state_date:
                    final_state_date = datetime.now()
                elif (datetime.now() - final_state_date) \
                        > timedelta(seconds=WAIT_AFTER_FINAL_STATE):
                    finished = True

            product_logs = self.retrieve_logs(product)
            log = None
            for log in product_logs.logs:
                if last_entry_date:
                    if log.timestamp <= last_entry_date:
                        continue
                yield log

            if log is not None:
                last_entry_date = log.timestamp

            if not finished:
                time.sleep(WAIT_BETWEEN_CALLS)
