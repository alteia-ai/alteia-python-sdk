.. _projects:

Projects
=========

Create a project
-----------------

.. doctest::

   >>> my_project = sdk.projects.create(name="My project", company="5d1a14af0422ae12d644a921")

See the :py:class:`projects.create() <alteia.apis.client.projectmngt.projectsimpl.ProjectsImpl.create>` documentation.

Delete a project
-----------------

To delete a project:

.. doctest::

   >>> sdk.projects.delete('5d1a14af0422ae12d537af02')

See the :py:class:`projects.delete() <alteia.apis.client.projectmngt.projectsimpl.ProjectsImpl.delete>` documentation.
