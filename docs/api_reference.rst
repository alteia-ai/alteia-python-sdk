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

.. autoclass:: alteia.core.config.Config
   :members: __init__

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

Annotations
===========

.. autoclass:: alteia.apis.client.annotations.annotationsimpl.AnnotationsImpl
   :members:

Comments
========

.. autoclass:: alteia.apis.client.comments.commentsimpl.CommentsImpl
   :members:

Datasets
========

.. autoclass:: alteia.apis.client.datamngt.datasetsimpl.DatasetsImpl
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

Projects
========
.. autoclass:: alteia.apis.client.projectmngt.projectsimpl.ProjectsImpl
   :members:

Project resource
----------------

.. autoclass:: alteia.core.resources.projectmngt.projects.Project
   :members: __init__

Tags
====

.. autoclass:: alteia.apis.client.tags.tagsimpl.TagsImpl
   :members:
