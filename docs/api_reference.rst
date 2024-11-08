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

Analytic Configurations
=======================

.. autoclass:: alteia.apis.client.analytics.configurationsimpl.AnalyticConfigurationsImpl
   :members:

Annotations
===========

.. autoclass:: alteia.apis.client.annotations.annotationsimpl.AnnotationsImpl
   :members:

Assessment Parameter Estimations
===========

.. autoclass:: alteia.apis.client.seasonplanner.assessmentparameterestimationsimpl.AssessmentParameterEstimationsImpl
   :members:

Assessment Parameter Variables
===========

.. autoclass:: alteia.apis.client.seasonplanner.assessmentparametervariablesimpl.AssessmentParameterVariablesImpl
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

.. autoclass:: alteia.apis.client.credentials.credentialsimpl.CredentialsImpl
   :members:

Crops
===========

.. autoclass:: alteia.apis.client.seasonplanner.cropsimpl.CropsImpl
   :members:

Datasets
========

.. autoclass:: alteia.apis.client.datamngt.datasetsimpl.DatasetsImpl
   :members:

Estimations Methods
========

.. autoclass:: alteia.apis.client.seasonplanner.estimationmethodsimpl.EstimationMethodsImpl
   :members:

Features
========

.. autoclass:: alteia.apis.client.featuresservice.featuresimpl.FeaturesImpl
   :members:

Fields
========

.. autoclass:: alteia.apis.client.seasonplanner.fieldsimpl.FieldsImpl
   :members:

Flights
========

.. autoclass:: alteia.apis.client.projectmngt.flightsimpl.FlightsImpl
   :members:

Flight resource
----------------

.. autoclass:: alteia.core.resources.projectmngt.flights.Flight
   :members: __init__

Growth Stages
========

.. autoclass:: alteia.apis.client.seasonplanner.growthstagesimpl.GrowthStagesImpl
   :members:

Missions
========

.. autoclass:: alteia.apis.client.projectmngt.missionsimpl.MissionsImpl
   :members:

Mission resource
----------------

.. autoclass:: alteia.core.resources.projectmngt.missions.Mission
   :members: __init__

Pilots
==============

.. autoclass:: alteia.apis.client.datacapture.pilotsimpl.PilotsImpl
   :members:

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

Season Planner Missions
========

.. autoclass:: alteia.apis.client.seasonplanner.seasonplannermissionsimpl.SeasonPlannerMissionsImpl
   :members:

Sensors
==============

.. autoclass:: alteia.apis.client.datacapture.sensorsimpl.SensorsImpl
   :members:

Sensors Models
==============

.. autoclass:: alteia.apis.client.datacapture.sensorsmodelsimpl.SensorsModelsImpl
   :members:

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

Trials
========

.. autoclass:: alteia.apis.client.seasonplanner.trialsimpl.TrialsImpl
   :members:

Users
=====

.. autoclass:: alteia.apis.client.auth.usersimpl.UsersImpl
   :members:

Datastream template
===================

.. autoclass:: alteia.apis.client.datastreamtemplate.datastreamtemplateimpl.DatastreamTemplateImpl
   :members:

Datastream
==========

.. autoclass:: alteia.apis.client.datastream.datastreamimpl.DatastreamImpl
   :members:
