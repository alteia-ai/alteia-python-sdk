.. _projects:

Projects
========

Create a project
-----------------

.. doctest::

   >>> my_project = sdk.projects.create(name='My project',
   ...                                  company='5d1a14af0422ae12d644a921')

See the :py:class:`projects.create() <alteia.apis.client.projectmngt.projectsimpl.ProjectsImpl.create>` documentation.

Describe a project
------------------

To describe a project or a list of projects:

.. doctest::

   >>> my_project = sdk.projects.describe('5d1a14af0422ae12d537af02')
   >>> my_projects = sdk.projects.describe(['5d1a14af0422ae12d537af02',
   ...                                      '5d1a14af0422ae12d537af05'])

See the :py:class:`projects.describe() <alteia.apis.client.projectmngt.projectsimpl.ProjectsImpl.describe>` documentation.

Update a project
----------------

To update the name of a project:

.. doctest::

   >>> my_updated_project = sdk.projects.update_name('5d1a14af0422ae12d537af02',
   ...                                               name='new name')

See the :py:class:`projects.update_name() <alteia.apis.client.projectmngt.projectsimpl.ProjectsImpl.update_name>` documentation.

To update the location of a project and fix it:

.. doctest::

   >>> my_updated_project = sdk.projects.update_location('5d1a14af0422ae12d537af02',
   ...                                                   location=[-114.06, 51.05],
   ...                                                   fixed=True)

See the :py:class:`projects.update_location() <alteia.apis.client.projectmngt.projectsimpl.ProjectsImpl.update_location>` documentation.

To update the SRS of a project:

.. doctest::

   >>> my_srs = 'PROJCS[...'  # use a valid WKT
   >>> my_updated_project = sdk.projects.update_srs('5d1a14af0422ae12d537af02',
   ...                                              horizontal_srs_wkt=my_srs)

See the :py:class:`projects.update_srs() <alteia.apis.client.projectmngt.projectsimpl.ProjectsImpl.update_srs>` documentation.

Delete a project
----------------

To delete a project:

.. doctest::

   >>> sdk.projects.delete('5d1a14af0422ae12d537af02')

See the :py:class:`projects.delete() <alteia.apis.client.projectmngt.projectsimpl.ProjectsImpl.delete>` documentation.

Search projects
---------------

Search the first 20 projects with `awesome` in the name, sort by newest first:

.. doctest::

   >>> my_filters = {'name': {'$match': 'awesome'}}
   >>> my_sort = {'creation_date': -1}
   >>> sdk.projects.search(filter=my_filters, sort=my_sort, limit=20)

Search the second page of same request:

.. doctest::

   >>> sdk.projects.search(filter=my_filters, sort=my_sort, limit=20, page=2)

See the :py:class:`projects.search() <alteia.apis.client.projectmngt.projectsimpl.ProjectsImpl.search>` documentation.

Do some stuff for all results, without using pages but using iterator:

.. doctest::

   >>> sg = sdk.projects.search_generator(filter=my_filters, sort=my_sort)
   >>> for project in sg:
   ...     print(project.name)

See the :py:class:`projects.search_generator() <alteia.apis.client.projectmngt.projectsimpl.ProjectsImpl.search_generator>` documentation.
