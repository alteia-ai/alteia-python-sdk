.. _missions:

Missions
========

Create a mission
----------------

.. doctest::

   >>> my_flight, my_mission = sdk.missions.create(
   ...     name='My mission',
   ...     project='5d1a14af0422ae12d537af02',
   ...     survey_date='2019-01-01T00:00:00.000Z',
   ...     number_of_images=2,
   ... )


See the :py:class:`missions.create() <alteia.apis.client.projectmngt.missionsimpl.MissionsImpl.create>` documentation.

Describe a mission
------------------

To describe a mission or a list of missions:

.. doctest::

   >>> my_mission = sdk.missions.describe('5d1a14af0422ae12d537af03')
   >>> my_missions = sdk.missions.describe(['5d1a14af0422ae12d537af03',
   ...                                      '5d1a14af0422ae12d537af06'])

See the :py:class:`missions.describe() <alteia.apis.client.projectmngt.missionsimpl.MissionsImpl.describe>` documentation.

Update a mission
----------------

To update the name of a mission:

.. doctest::

   >>> my_updated_mission = sdk.missions.update_name('5d1a14af0422ae12d537af03',
   ...                                               name='new name')

See the :py:class:`missions.update_name() <alteia.apis.client.projectmngt.missionsimpl.MissionsImpl.update_name>` documentation.

To update the survey date:

.. doctest::

   >>> my_updated_mission = sdk.missions.update_survey_date('5d1a14af0422ae12d537af03',
   ...                                                      survey_date='2019-01-03')

See the :py:class:`missions.update_survey_date() <alteia.apis.client.projectmngt.missionsimpl.MissionsImpl.update_survey_date>` documentation.

Delete a mission
----------------

To delete a mission:

.. doctest::

   >>> sdk.missions.delete('5d1a14af0422ae12d537af03')

See the :py:class:`missions.delete() <alteia.apis.client.projectmngt.missionsimpl.MissionsImpl.delete>` documentation.

Request for an archive of photos
--------------------------------

To ask for an archive creation for all images of a mission:

.. doctest::

   >>> sdk.missions.create_archive('5d1a14af0422ae12d537af03')

See the :py:class:`missions.create_archive() <alteia.apis.client.projectmngt.missionsimpl.MissionsImpl.create_archive>` documentation.

Search missions
---------------

Search the first 20 missions with `awesome` in the name, sort by newest first:

.. doctest::

   >>> my_filters = {'name': {'$match': 'awesome'}}
   >>> my_sort = {'creation_date': -1}
   >>> sdk.missions.search(filter=my_filters, sort=my_sort, limit=20)

Search the second page of same request:

.. doctest::

   >>> sdk.missions.search(filter=my_filters, sort=my_sort, limit=20, page=2)

See the :py:class:`missions.search() <alteia.apis.client.projectmngt.projectsimpl.MissionsImpl.search>` documentation.

Do some stuff for all results, without using pages but using iterator:

.. doctest::

   >>> sg = sdk.missions.search_generator(filter=my_filters, sort=my_sort)
   >>> for mission in sg:
   ...     print(mission.name)

See the :py:class:`missions.search_generator() <alteia.apis.client.projectmngt.MissionsImpl.ProjectsImpl.search_generator>` documentation.
