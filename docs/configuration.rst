.. _configuration:

===============
 Configuration
===============

The Alteia Python SDK has a unique entry point through the
:py:mod:`alteia.sdk.SDK` class. When instantiating
that class, one must provide credentials through:

- The keyword arguments
  :py:func:`alteia.sdk.SDK.__init__` function.

- A configuration file.

.. _keyword-arguments:

Keyword Arguments
=================

Here are the configurable properties:

- ``user`` - The user identifier. Required if not provided through a
  configuration file, nor using ``client_id``

- ``password`` - The account password. Required if not provided
  through a configuration file and ``user`` is used.

- ``client_id`` - An API client identifier. Required if not provided
  through a configuration file, nor using ``user``.

- ``secret`` - The API client secret. Required if not provided
  through a configuration file and ``client_id`` is used.

- ``access_token`` - An optional API access token to use to
  authenticate requests as an alternative to using ``user`` or
  ``client_id``.

- ``url`` - The public endpoint of Alteia. Default to
  https://app.alteia.com.

- ``connection`` - A dictionnary providing the connection
  configuration.

- ``proxy_url`` - An optional proxy URL (⚠️ will be overrided by the value of
  ``https_proxy`` or ``http_proxy`` environment variable if set).


The connection configuration can specify the default number of retries
through the key ``max_retries`` (the default is to retry each request
10 times with a backoff factor) and whether to disable check of SSL
certificates through the key ``disable_ssl_certificate`` (the default
is to disable such checks).

.. _configuration-file:

Configuration File
==================

Configuration can be read from a file. Configuration files must be
written using JSON format as a single JSON object. The supported
properties are the same as the one described in the
:ref:`keyword-arguments` section.

The path of the default configuration file depends on the operating
system and is documented with the
:py:class:`alteia.core.config.ConnectionConfig` class.

Example Configuration File
--------------------------

Here is a simple configuration file::

    {"user": "firstname.lastname@example.com",
     "password": "20h!nph-14-l2394"}

And a more complete one, specifying both a custom URL and connection
configurations::

    {
      "user": "firstname.lastname@example.com",
      "password": "20h!nph-14-12394",
      "url": "https://app.alteia.com",
      "connection": {
        "max_retries": 3,
        "disable_ssl_certificate": true
      },
      "proxy_url": "https://my-proxy.com:8888"
    }

Custom Configuration File
-------------------------

In case one has multiple accounts, it's possible to specify a custom
configuration file. For example, to instantiate a
:py:mod:`alteia.sdk.SDK` using the configuration found
in the ``~/.local/share/alteia/devconf.json`` file::

    import alteia
    sdk = alteia.SDK(config_path='~/.local/share/alteia/devconf.json')
