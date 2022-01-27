.. _how_to_upgrade:

================
 How to upgrade
================

This section adds information about how to change your code when you upgrade your SDK to newer versions.


From 1.3.x to 2.0.0
===================


Breaking changes
----------------

**Summary list of breaking changes**

- Change signature :py:class:`flights.search() <alteia.apis.client.projectmngt.flightsimpl.FlightsImpl.search>`: new usage with ``filter`` parameter. Delete ``project`` and ``mission`` parameters.
- Change signature :py:class:`missions.search() <alteia.apis.client.projectmngt.missionsimpl.MissionsImpl.search>`: new usage with ``filter`` parameter. Delete ``missions``, ``flights``, ``project`` and ``deleted`` parameters.
- Change signature :py:class:`projects.search() <alteia.apis.client.projectmngt.projectsimpl.ProjectsImpl.search>`: new usage with ``filter`` parameter. Delete ``name`` and ``deleted`` parameters.
- Delete ``missions.complete_survey_upload()``: use :py:class:`flights.update_status() <alteia.apis.client.projectmngt.flightsimpl.FlightsImpl.update_status>` instead.
- Delete ``missions.rename()``: use :py:class:`missions.update_name() <alteia.apis.client.projectmngt.missionsimpl.MissionsImpl.update_name>` instead.
- Delete ``projects.rename()``: use :py:class:`projects.update_name() <alteia.apis.client.projectmngt.projectsimpl.ProjectsImpl.update_name>` instead.
- Remove legacy ``company`` argument in :py:class:`share_tokens.search() <alteia.apis.client.auth.sharetokensimpl.ShareTokensImpl.search>`. Use ``filter`` instead.
- Remove legacy ``secret`` argument in SDK init. Use ``client_secret`` instead.


**How-to details**

Search projects by name:
    >>> # sdk 1.3.x
    >>> sdk.projects.search(name='my project')

    >>> # sdk 2.0.0
    >>> sdk.projects.search(filter={'name': {'$match': 'my project'}}, limit=10000)
    # Notes:
        - The `$match` is case insensitive, and diacritics insensitive.
        - You can use `$eq` to perform a strict name equality. `$match` find names which contains the search value.
        - Without `limit`, the method will return 100 first results (`search_generator()` can be used instead).

    See the :py:class:`projects.search() <alteia.apis.client.projectmngt.projectsimpl.ProjectsImpl.search>` and
    :py:class:`projects.search_generator() <alteia.apis.client.projectmngt.projectsimpl.ProjectsImpl.search_generator>` documentation.

Search projects including deleted ones (depends on your role):
    >>> # sdk 1.3.x
    >>> sdk.projects.search(deleted=True)

    >>> # sdk 2.0.0: it must be done in 2 different requests
    >>> sdk.projects.search()
    >>> sdk.projects.search(filter={'deletion_date': {'$exists': True}})

    See the :py:class:`projects.search() <alteia.apis.client.projectmngt.projectsimpl.ProjectsImpl.search>` and
    :py:class:`projects.search_generator() <alteia.apis.client.projectmngt.projectsimpl.ProjectsImpl.search_generator>` documentation.

Rename a project:
    >>> # sdk 1.3.x
    >>> sdk.projects.rename(my_project_id, 'new name')

    >>> # sdk 2.0.0
    >>> sdk.projects.update_name(my_project_id, 'new name')

    See the :py:class:`projects.update_name() <alteia.apis.client.projectmngt.projectsimpl.ProjectsImpl.update_name>` documentation.

Search multiple missions by IDs:
    >>> # sdk 1.3.x
    >>> sdk.missions.search(missions=[id1, id2, id3], deleted=True)

    >>> # sdk 2.0.0
    >>> sdk.missions.describe([id1, id2, id3])

    See the :py:class:`missions.describe() <alteia.apis.client.projectmngt.missionsimpl.MissionsImpl.describe>`  documentation.

Search missions by projects:
    >>> # sdk 1.3.x
    >>> sdk.missions.search(projects=[id1, id2, id3])

    >>> # sdk 2.0.0
    >>> sdk.missions.search(filter={'project': {'$in': [id1, id2, id3]}}, limit=10000)
    # Notes:
        - With only one project ID, you can use `{'$eq': id1}`.
        - Without `limit`, the method will return 100 first results (`search_generator()` can be used instead)

    See the :py:class:`missions.search() <alteia.apis.client.projectmngt.missionsimpl.MissionsImpl.search>` and
    :py:class:`missions.search_generator() <alteia.apis.client.projectmngt.missionsimpl.MissionsImpl.search_generator>` documentation.

Search missions having at least one of the wanted flights:
    >>> # sdk 1.3.x
    >>> sdk.missions.search(flights=[id1, id2, id3])

    >>> # sdk 2.0.0
    >>> sdk.missions.search(filter={'flights': {'$in': [id1, id2, id3]}}, limit=10000)
    # Notes:
        - Without `limit`, the method will return 100 first results (`search_generator()` can be used instead)

    See the :py:class:`missions.search() <alteia.apis.client.projectmngt.missionsimpl.MissionsImpl.search>` and
    :py:class:`missions.search_generator() <alteia.apis.client.projectmngt.missionsimpl.MissionsImpl.search_generator>` documentation.

Search missions including deleted ones (depends on your role):
    >>> # sdk 1.3.x
    >>> sdk.missions.search(deleted=True)

    >>> # sdk 2.0.0: it must be done in 2 different requests
    >>> sdk.missions.search()
    >>> sdk.missions.search(filter={'deletion_date': {'$exists': True}})

    See the :py:class:`missions.search() <alteia.apis.client.projectmngt.missionsimpl.MissionsImpl.search>` and
    :py:class:`missions.search_generator() <alteia.apis.client.projectmngt.missionsimpl.MissionsImpl.search_generator>` documentation.

Rename a mission:
    >>> # sdk 1.3.x
    >>> sdk.missions.rename(my_mission_id, 'new name')

    >>> # sdk 2.0.0
    >>> sdk.missions.update_name(my_mission_id, 'new name')

    See the :py:class:`missions.update_name() <alteia.apis.client.projectmngt.missionsimpl.MissionsImpl.update_name>` documentation.

Complete a survey upload:
    >>> # sdk 1.3.x
    >>> sdk.missions.complete_survey_upload(my_flight_id)

    >>> # sdk 2.0.0
    >>> sdk.flights.update_status(my_flight_id, status='completed')

    See the :py:class:`flights.update_status() <alteia.apis.client.projectmngt.flightsimpl.FlightsImpl.update_status>` documentation.

Search flights by project:
    >>> # sdk 1.3.x
    >>> sdk.flights.search(project=id1)

    >>> # sdk 2.0.0
    >>> sdk.flights.search(filter={'project': {'$eq': id1}}, limit=10000)
    # Notes:
        - With multiple project IDs, you can use `{'$in': [id1, id2, id3]}`.
        - Without `limit`, the method will return 100 first results (`search_generator()` can be used instead)

    See the :py:class:`flights.search() <alteia.apis.client.projectmngt.flightsimpl.FlightsImpl.search>` and
    :py:class:`flights.search_generator() <alteia.apis.client.projectmngt.flightsimpl.FlightsImpl.search_generator>` documentation.

Search flights by mission:
    >>> # sdk 1.3.x
    >>> sdk.flights.search(mission=id1)

    >>> # sdk 2.0.0
    >>> sdk.flights.search(filter={'mission': {'eq': id1}}, limit=10000)
    # Notes:
        - With multiple mission IDs, you can use `{'$in': [id1, id2, id3]}`.
        - Without `limit`, the method will return 100 first results (`search_generator()` can be used instead)

    See the :py:class:`flights.search() <alteia.apis.client.projectmngt.flightsimpl.FlightsImpl.search>` and
    :py:class:`flights.search_generator() <alteia.apis.client.projectmngt.flightsimpl.FlightsImpl.search_generator>` documentation.

Search share tokens by company:
    >>> # sdk 1.3.x
    >>> sdk.share_tokens.search(company=id1)

    >>> # sdk 2.0.0
    >>> sdk.share_tokens.search(filter={'company': {'eq': id1}})

    See the :py:class:`share_tokens.search() <alteia.apis.client.auth.sharetokensimpl.ShareTokensImpl.search>` and
    :py:class:`share_tokens.search_generator() <alteia.apis.client.auth.sharetokensimpl.ShareTokensImpl.search_generator>` documentation.


Init SDK using client and secret:
    >>> # sdk 1.3.x
    >>> sdk = SDK(client_id='...', secret='...')

    >>> # sdk 2.0.0
    >>> sdk = SDK(client_id='...', client_secret='...')


Improvements
------------

Describe multiple projects:
    >>> # sdk 1.3.x
    >>> sdk.projects.describe(id1)
    >>> sdk.projects.describe(id2)
    >>> sdk.projects.describe(id3)

    >>> # sdk 2.0.0
    >>> sdk.missions.describe([id1, id2, id3])

    See the :py:class:`projects.describe() <alteia.apis.client.projectmngt.projectsimpl.ProjectsImpl.describe>` documentation.

Describe multiple missions:
    >>> # sdk 1.3.x
    >>> sdk.missions.describe(id1)
    >>> sdk.missions.describe(id2)
    >>> sdk.missions.describe(id3)

    >>> # sdk 2.0.0
    >>> sdk.missions.describe([id1, id2, id3])

    See the :py:class:`missions.describe() <alteia.apis.client.projectmngt.missionsimpl.MissionsImpl.describe>`  documentation.

Describe multiple flights:
    >>> # sdk 1.3.x
    >>> sdk.flights.describe(id1)
    >>> sdk.flights.describe(id2)
    >>> sdk.flights.describe(id3)

    >>> # sdk 2.0.0
    >>> sdk.flights.describe([id1, id2, id3])

    See the :py:class:`flights.describe() <alteia.apis.client.projectmngt.flightsimpl.FlightsImpl.describe>` documentation.

Good practice: for own user scripts (run in local), set the name of the script to log it in requests:
    >>> # sdk 1.3.x
    >>> sdk = SDK(...)

    >>> # sdk 2.0.0
    >>> sdk = SDK(..., service='MyBeautifulScript/1.0.0')
