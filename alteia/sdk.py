import logging
import os
from typing import Optional

from alteia.apis.client.analytics.analyticsimpl import AnalyticsImpl
from alteia.apis.client.analytics.productsimpl import ProductsImpl
from alteia.apis.client.annotations.annotationsimpl import AnnotationsImpl
from alteia.apis.client.auth.companiesimpl import CompaniesImpl
from alteia.apis.client.auth.oauthclientsimpl import OAuthClientsImpl
from alteia.apis.client.auth.sharetokensimpl import ShareTokensImpl
from alteia.apis.client.auth.usersimpl import UsersImpl
from alteia.apis.client.comments.commentsimpl import CommentsImpl
from alteia.apis.client.datacapture.carriersimpl import CarriersImpl
from alteia.apis.client.datacapture.carriersmodelsimpl import CarrierModelsImpl
from alteia.apis.client.datacapture.collectiontasksimpl import \
    CollectionTaskImpl
from alteia.apis.client.datacapture.teamsimpl import TeamsImpl
from alteia.apis.client.datamngt.datasetsimpl import DatasetsImpl
from alteia.apis.client.externalproviders.credentialsimpl import \
    CredentialsImpl
from alteia.apis.client.featuresservice.collectionsimpl import CollectionsImpl
from alteia.apis.client.featuresservice.featuresimpl import FeaturesImpl
from alteia.apis.client.projectmngt.flightsimpl import FlightsImpl
from alteia.apis.client.projectmngt.missionsimpl import MissionsImpl
from alteia.apis.client.projectmngt.projectsimpl import ProjectsImpl
from alteia.apis.client.tags.tagsimpl import TagsImpl
from alteia.apis.provider import (AnalyticsServiceAPI, AnnotationsAPI,
                                  AssetManagementAPI, AuthAPI,
                                  CollectionTaskAPI,
                                  CollectionTaskManagementAPI,
                                  DataManagementAPI,
                                  ExternalProviderServiceAPI,
                                  FeaturesServiceAPI, ProjectManagerAPI,
                                  UIServicesAPI)
from alteia.core.config import ConnectionConfig
from alteia.core.connection.connection import Connection
from alteia.core.connection.credentials import (ClientCredentials, Credentials,
                                                UserCredentials)
from alteia.core.errors import ConfigError
from alteia.core.utils.utils import prompt_user
from alteia.core.utils.warnings import warn_for_deprecation

__all__ = ('SDK', )

LOGGER = logging.getLogger(__name__)


def _get_credentials(config: ConnectionConfig) -> Optional[Credentials]:
    if config.user is not None:
        LOGGER.debug('Using user credentials')
        return UserCredentials(config.user, config.password,
                               client_id=config.client_id,
                               client_secret=config.client_secret)
    elif config.client_id:
        LOGGER.debug('Using APIs client credentials')
        return ClientCredentials(config.client_id,
                                 config.client_secret)
    return None


def _create_connection(config: ConnectionConfig,
                       credentials: Optional[Credentials]) -> Connection:
    LOGGER.info('Initializing connection')
    access_token = config.access_token

    if config.url is None:
        LOGGER.error('Base url not found')
        raise ConfigError('Missing url')

    conn_opts = {'base_url': config.url,
                 'credentials': credentials,
                 'access_token': access_token}

    if config.proxy_url is not None:
        LOGGER.info(f'Use proxy {config.proxy_url!r}')
        conn_opts.update({'proxy_url': config.proxy_url})

    if config.connection is not None:
        for key in ('disable_ssl_certificate', 'max_retries'):
            if key in config.connection:
                conn_opts.update({key: config.connection[key]})

    if credentials is None and access_token is None:
        LOGGER.error('Credentials and access token not found')
        raise ConfigError('Credentials or access token expected')

    try:
        return Connection(**conn_opts)
    except Exception as e:
        LOGGER.error(f'Cannot establish a connection: {e}')
        raise e


class SDK():
    """Entry point providing access to resource managers.

    Resource managers are availables as instance attributes.
    The ``dir`` builtin can be used to list the availables managers.

    The following examples show various ways to instantiate that
    class:

    - Using a username and a password::

        >>> sdk = SDK(user='admin1', password='password')

    - Using an OAuth client identifier and secret::

        >>> sdk = SDK(client_id='72a5f676-6efc-48c5-ac07-4c534c3cdccc',
                      client_secret='52ccd77d-17e4-499b-995e-3a2731550723')

    - Using a configuration file::

        >>> sdk = SDK(config_path='~/.local/share/alteia/conf.json')

    """
    def __init__(self,  *, config_path: str = None,
                 user: str = None, password: str = None,
                 client_id: str = None, client_secret: str = None,
                 url: str = None,
                 proxy_url: str = None, force_prompt: bool = False, **kwargs):
        """Initializes Alteia Python SDK entry point.

        Args:
            config_path: Optional path to a custom configuration file.

            user: Optional username (email).

            password: Optional password (mandatory if ``username`` is defined).

            client_id: Optional OAuth client identifier.

            client_secret: Optional OAuth client secret (mandatory if
                ``client_id`` is defined).

            url: Optional platform URL (default ``https://app.alteia.com``).

            proxy_url: Optional proxy URL.

            force_prompt: Option to force the user to set or confirm his connection
                info through the prompt.

            kwargs: Optional keyword arguments to merge with
                           the configuration.

        """
        LOGGER.info('Initializing SDK')

        # Support for legacy secret argument
        if 'secret' in kwargs:
            client_secret = kwargs.pop('secret')
            warn_for_deprecation('Support for `secret` argument', target='2.0.0')

        connection_params = kwargs

        # Only keep defined parameters
        for param_name, value in (('file_path', config_path),
                                  ('user', user),
                                  ('password', password),
                                  ('client_id', client_id),
                                  ('client_secret', client_secret),
                                  ('url', url),
                                  ('proxy_url', proxy_url)):
            if value is not None:
                connection_params[param_name] = value

        for env_var in ('https_proxy', 'HTTPS_PROXY',
                        'http_proxy', 'HTTP_PROXY'):
            env_var_value = os.environ.get(env_var)
            if env_var_value is not None:
                connection_params['proxy_url'] = env_var_value
                LOGGER.info(f'Found environment variable {env_var!r} with value: {env_var_value!r}')
                break

        connection_config = ConnectionConfig(**connection_params)

        if force_prompt:
            url = prompt_user(
                'Platform URL',
                current_value=getattr(connection_config, 'url', None),
            )
            email = prompt_user(
                'Email',
                current_value=getattr(connection_config, 'user', None),
            )
            password = prompt_user(
                'Password (will be hidden)',
                current_value=getattr(connection_config, 'password', None),
                hidden=True
            )

            connection_params.update({
                'url': url,
                'user': email,
                'password': password
            })
            connection_config = ConnectionConfig(**connection_params)

        credentials = _get_credentials(connection_config)
        self._connection = _create_connection(connection_config, credentials)

        token = self._connection._token_manager.token
        if not token.access_token or not token.token_type:
            self._connection._renew_token()

        self.__set_providers()
        self.__set_resources_as_attributes()

    def __set_providers(self):
        provider_args = {'connection': self._connection}
        self._providers = {
            'analytics_service_api': AnalyticsServiceAPI(**provider_args),
            'annotations_api': AnnotationsAPI(**provider_args),
            'asset_management_api': AssetManagementAPI(**provider_args),
            'auth_api': AuthAPI(**provider_args),
            'collection_task_api': CollectionTaskAPI(**provider_args),
            'collection_task_management_api': CollectionTaskManagementAPI(**provider_args),
            'data_management_api': DataManagementAPI(**provider_args),
            'external_provider_service_api': ExternalProviderServiceAPI(**provider_args),
            'project_manager_api': ProjectManagerAPI(**provider_args),
            'ui_services_api': UIServicesAPI(**provider_args),
            'features_service_api': FeaturesServiceAPI(**provider_args),
        }

    def __set_resources_as_attributes(self):
        kwargs = {'sdk': self}
        kwargs.update(self._providers)

        self.analytics: AnalyticsImpl = AnalyticsImpl(**kwargs)
        self.annotations: AnnotationsImpl = AnnotationsImpl(**kwargs)
        self.carriers: CarriersImpl = CarriersImpl(**kwargs)
        self.carrier_models: CarrierModelsImpl = CarrierModelsImpl(**kwargs)
        self.collection_tasks: CollectionTaskImpl = CollectionTaskImpl(**kwargs)
        self.comments: CommentsImpl = CommentsImpl(**kwargs)
        self.companies: CompaniesImpl = CompaniesImpl(**kwargs)
        self.credentials: CredentialsImpl = CredentialsImpl(**kwargs)
        self.datasets: DatasetsImpl = DatasetsImpl(**kwargs)
        self.flights: FlightsImpl = FlightsImpl(**kwargs)
        self.missions: MissionsImpl = MissionsImpl(**kwargs)
        self.oauth_clients: OAuthClientsImpl = OAuthClientsImpl(**kwargs)
        self.products: ProductsImpl = ProductsImpl(**kwargs)
        self.projects: ProjectsImpl = ProjectsImpl(**kwargs)
        self.share_tokens: ShareTokensImpl = ShareTokensImpl(**kwargs)
        self.tags: TagsImpl = TagsImpl(**kwargs)
        self.teams: TeamsImpl = TeamsImpl(**kwargs)
        self.users: UsersImpl = UsersImpl(**kwargs)
        self.collections: CollectionsImpl = CollectionsImpl(**kwargs)
        self.features: FeaturesImpl = FeaturesImpl(**kwargs)
