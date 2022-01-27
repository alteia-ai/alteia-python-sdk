.. _first_steps:

=============
 First steps
=============

.. _installation:

Installation
==============

Install the latest Alteia Python package release via :command:`pip`:

.. code-block:: bash

   pip install alteia

Configuration
==============

To use the SDK, you must configure your Alteia credentials.

To do that, just create a ``config-connection.json`` configuration file:

.. code-block:: json

   {
     "user": "YOUR_EMAIL_ADDRESS",
     "password": "YOUR_ALTEIA_PASSWORD"
   }

Depending on your operating system, create the following directory and save the ``config-connection.json`` file in:

- **(Windows)** ``%USERPROFILE%\Application\Application Data\Alteia\alteia\``
- **(Linux)** ``~/.local/share/alteia/``
- **(MacOS)** ``~/Library/Application Support/alteia/``

.. note::
   See the chapter on :ref:`configuration` for more details about the configuration files.

Using the SDK
==============

.. testsetup:: *

   import alteia
   sdk = alteia.SDK()

Any usage starts with the creation of a :py:mod:`alteia.sdk.SDK` instance::

   >>> import alteia
   >>> sdk = alteia.SDK()

.. note::

   Alternatively, if you don't want to use the SDK `with the credentials saved in the default configuration file <#configuration>`_, you can pass your credentials directly, with:

   .. code-block:: python

      >>> import alteia
      >>> sdk = alteia.SDK(url="https://app.alteia.com/",
      ...                  user="YOUR_EMAIL_ADDRESS",
      ...                  password="YOUR_ALTEIA_PASSWORD")


Get all the projects available
-------------------------------

.. doctest::

   >>> projects = sdk.projects.search(limit=100)

See the :py:class:`projects.search() <alteia.apis.client.projectmngt.projectsimpl.ProjectsImpl.search>` documentation.

Get the missions of a project
------------------------------

.. doctest::

   >>> my_project = sdk.projects.search(filter={'name': {'$eq': 'My_project'}})[0]
   >>> missions = sdk.missions.search(filter={'project': {'$eq': my_project.id}})

See the :py:class:`missions.search() <alteia.apis.client.projectmngt.missionsimpl.MissionsImpl.search>` documentation.

Search for datasets related to a mission
-----------------------------------------

.. doctest::

   >>> my_mission = missions[0]
   >>> datasets = sdk.datasets.search(filter={'mission': {'$eq': my_mission.id}})

See the :py:class:`datasets.search() <alteia.apis.client.datamngt.datasetsimpl.DatasetsImpl.search>` documentation.

Explore the dataset properties
-------------------------------

Let's print some properties of a dataset:

.. doctest::

   >>> my_dataset = datasets[0]
   >>> print("Name: {}".format(my_dataset.name))
   >>> print("Type: {}".format(my_dataset.type))
   >>> print("Creation date: {}".format(my_dataset.creation_date))


Some dataset properties depend on its type (``image``, ``raster``, ``mesh``, ``pcl``, ``vector``, ``file``).
You can list all the available properties for a dataset with:

.. doctest::

   >>> dir(my_dataset)

To look for the files related to a dataset, we can list the dataset components:

.. doctest::

   >>> print(my_dataset.components)

Download a dataset component
-----------------------------

To download a dataset component in the current directory:

.. doctest::

   >>> component = my_dataset.components[0]
   >>> sdk.datasets.download_component(dataset=my_dataset.id,
   ...                                 component=component.get("name"))


See the :py:class:`datasets.download_component() <alteia.apis.client.datamngt.datasetsimpl.DatasetsImpl.download_component>` documentation.

Create a new dataset
---------------------

To create a new ``file`` dataset related to a project:

.. doctest::

   >>> new_dataset = sdk.datasets.create_file_dataset(name='My file dataset',
   ...                                                project=my_project.id)

See the :py:class:`datasets.create_file_dataset() <alteia.apis.client.datamngt.datasetsimpl.DatasetsImpl.create_file_dataset>` documentation.

And upload a file:

.. doctest::

   >>> file_to_upload = "/replace/with/a/file_path.ext"
   >>> sdk.datasets.upload_file(dataset=new_dataset.id,
   ...                          component='file',
   ...                          file_path=file_to_upload)

See the :py:class:`datasets.upload_file() <alteia.apis.client.datamngt.datasetsimpl.DatasetsImpl.upload_file>` documentation.

Add a tag
----------

Let's add a tag on the dataset created.

.. doctest::

   >>> my_tag = sdk.tags.create(name='My tag',
   ...                          project=my_project.id,
   ...                          type='dataset',
   ...                          target=new_dataset.id)

See the :py:class:`tags.create() <alteia.apis.client.tags.tagsimpl.TagsImpl.create>` documentation.

This tag can be deleted with:

.. doctest::

   >>> sdk.tags.delete(my_tag.id)

See the :py:class:`tags.delete() <alteia.apis.client.tags.tagsimpl.TagsImpl.delete>` documentation.


Add a comment
-------------

To add a comment on this dataset:

.. doctest::

   >>> my_comment = sdk.comments.create(text='This is my first dataset',
   ...                                  project=my_project.id,
   ...                                  type='dataset',
   ...                                  target=new_dataset.id)

See the :py:class:`comments.create() <alteia.apis.client.comments.commentsimpl.CommentsImpl.create>` documentation.

We can mark all the comments of this dataset as read with:

.. doctest::

   >>> sdk.comments.mark_as_read(project=my_project.id,
   ...                           type='dataset',
   ...                           target=new_dataset.id)

See the :py:class:`comments.mark_as_read() <alteia.apis.client.comments.commentsimpl.CommentsImpl.mark_as_read>` documentation.


Add an annotation
------------------

It is also possible to add an annotation to a project. For example,
let's create one whose geometry is the bounding box of the project:

.. doctest::

   >>> a = sdk.annotations.create(project=my_project.id,
   ...                            geometry=my_project.real_bbox,
   ...                            name='Project bounding box',
   ...                            description='Bounding box around the project')

See the :py:class:`annotations.create() <alteia.apis.client.annotations.annotationsimpl.AnnotationsImpl.create>` documentation.

This annotation can be deleted with:

.. doctest::

   >>> sdk.annotations.delete(a.id)

See the :py:class:`annotations.delete() <alteia.apis.client.annotations.annotationsimpl.AnnotationsImpl.delete>` documentation.
