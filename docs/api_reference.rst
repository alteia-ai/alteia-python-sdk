.. _api_reference:

===============
 API Reference
===============

This section covers interfaces of Alteia Python SDK.

Main interface
==============

Entry point
-----------

Alteia Python SDK has a unique entry point: The class
``SDK``.

.. autoclass:: alteia.sdk.SDK
   :members: __init__

Configuration
-------------

.. autoclass:: alteia.core.config.ConnectionConfig
   :members: __init__

Resources management
--------------------

.. autoclass:: alteia.core.resources.resource.Resource
   :members: __init__

Errors
------

.. automodule:: alteia.core.errors
   :members:

Analytics
=========

.. autoclass:: alteia.apis.client.analytics.analyticsimpl.AnalyticsImpl
   :members:

Annotations
===========

.. autoclass:: alteia.apis.client.annotations.annotationsimpl.AnnotationsImpl
   :members:

Carriers
========

.. autoclass:: alteia.apis.client.datacapture.carriersimpl.CarriersImpl
   :members:

Carrier models
==============

.. autoclass:: alteia.apis.client.datacapture.carriersmodelsimpl.CarrierModelsImpl
   :members:

Collections
===========

.. autoclass:: alteia.apis.client.featuresservice.collectionsimpl.CollectionsImpl
   :members:

Collection tasks
================

.. autoclass:: alteia.apis.client.datacapture.collectiontasksimpl.CollectionTaskImpl
   :members:

Comments
========

.. autoclass:: alteia.apis.client.comments.commentsimpl.CommentsImpl
   :members:

Companies
=========

.. autoclass:: alteia.apis.client.auth.companiesimpl.CompaniesImpl
   :members:

Credentials
===========

.. autoclass:: alteia.apis.client.externalproviders.credentialsimpl.CredentialsImpl
   :members:

Datasets
========

.. autoclass:: alteia.apis.client.datamngt.datasetsimpl.DatasetsImpl
   :members:

Features
========

.. autoclass:: alteia.apis.client.featuresservice.featuresimpl.FeaturesImpl
   :members:

Missions
========

.. autoclass:: alteia.apis.client.projectmngt.missionsimpl.MissionsImpl
   :members:

Mission resource
----------------

.. autoclass:: alteia.core.resources.projectmngt.missions.Mission
   :members: __init__

Flight resource
----------------

.. autoclass:: alteia.core.resources.projectmngt.flights.Flight
   :members: __init__

Products
========
.. autoclass:: alteia.apis.client.analytics.productsimpl.ProductsImpl
   :members:


Projects
========
.. autoclass:: alteia.apis.client.projectmngt.projectsimpl.ProjectsImpl
   :members:

Project resource
----------------

.. autoclass:: alteia.core.resources.projectmngt.projects.Project
   :members: __init__

Share tokens
============

.. autoclass:: alteia.apis.client.auth.sharetokensimpl.ShareTokensImpl
   :members:

Tags
====

.. autoclass:: alteia.apis.client.tags.tagsimpl.TagsImpl
   :members:

Teams
=====

.. autoclass:: alteia.apis.client.datacapture.teamsimpl.TeamsImpl
   :members:

Users
=====

.. autoclass:: alteia.apis.client.auth.usersimpl.UsersImpl
   :members:
