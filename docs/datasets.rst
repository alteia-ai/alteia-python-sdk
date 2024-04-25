.. _datasets:

Datasets
=========

Create an image dataset
------------------------

To create an ``image`` dataset:

.. doctest::

   >>> my_dataset = sdk.datasets.create_image_dataset(
   ...     name='My Image',
   ...     project=PROJECT_ID,
   ...     mission=MISSION_ID,
   ...     geometry={'type': 'Point', 'coordinates': [LONGITUDE, LATITUDE]},
   ...     width=IMAGE_WIDTH_IN_PIXELS,
   ...     height=IMAGE_HEIGHT_IN_PIXELS
   ... )

See the :py:class:`datasets.create_image_dataset() <alteia.apis.client.datamngt.datasetsimpl.DatasetsImpl.create_image_dataset>` documentation.

And upload the image file:

.. doctest::

   >>> file_to_upload = '/path/to/image/file.jpg'
   >>> sdk.datasets.upload_file(dataset=my_dataset.id,
   ...                          component='image',
   ...                          file_path=file_to_upload)

See the :py:class:`datasets.upload_file() <alteia.apis.client.datamngt.datasetsimpl.DatasetsImpl.upload_file>` documentation.documentation.

Options
~~~~~~~

* `parse_metadata`: Boolean that automatically parses the Exif & XMP data from the image and updates the corresponding dataset attributes. In case of `None` or `True` the platform will automatically parse the ingested dataset.

Create a point cloud dataset
-----------------------------

To create a point cloud (``pcl``) dataset:

.. doctest::

   >>> my_dataset = sdk.datasets.create_pcl_dataset(name='My PCL',
   ...                                              project=PROJECT_ID,
   ...                                              mission=MISSION_ID)

See the :py:class:`datasets.create_pcl_dataset() <alteia.apis.client.datamngt.datasetsimpl.DatasetsImpl.create_pcl_dataset>` documentation.

And upload the pcl file:

.. doctest::

   >>> file_to_upload = '/path/to/pcl/file.las'
   >>> sdk.datasets.upload_file(dataset=my_dataset.id,
   ...                          component='pcl',
   ...                          file_path=file_to_upload)

See the :py:class:`datasets.upload_file() <alteia.apis.client.datamngt.datasetsimpl.DatasetsImpl.upload_file>` documentation.

Create a vector dataset
------------------------

To create a ``vector`` dataset with a specific CRS (here ``UTM 32631``):

.. doctest::

   >>> my_dataset = sdk.datasets.create_vector_dataset(
   ...     name='My Vector',
   ...     project=PROJECT_ID,
   ...     mission=MISSION_ID,
   ...     dataset_format='shapefile',
   ...     is_archive=True,
   ...     horizontal_srs_wkt='PROJCS["WGS 84 / UTM zone 31N",GEOGCS["WGS 84",[...]',
   ...     # Full WKT available on http://epsg.io/32631.wkt
   ... )


See the :py:class:`datasets.create_vector_dataset() <alteia.apis.client.datamngt.datasetsimpl.DatasetsImpl.create_vector_dataset>` documentation.

And upload the vector file (here a **shapefile**):

.. doctest::

   >>> file_to_upload = '/path/to/vector/shapefile.zip'
   >>> sdk.datasets.upload_file(dataset=my_dataset.id,
   ...                          component='archive',
   ...                          file_path=file_to_upload)

See the :py:class:`datasets.upload_file() <alteia.apis.client.datamngt.datasetsimpl.DatasetsImpl.upload_file>` documentation.documentation.

Create a mesh dataset
----------------------

To create a ``mesh`` dataset **with two texture files** (and one material file, which is the default value):

.. doctest::

   >>> my_dataset = sdk.datasets.create_mesh_dataset(name='My Mesh',
   ...                                               project=PROJECT_ID,
   ...                                               mission=MISSION_ID,
   ...                                               texture_count=2)

See the :py:class:`datasets.create_mesh_dataset() <alteia.apis.client.datamngt.datasetsimpl.DatasetsImpl.create_mesh_dataset>` documentation.

And upload the mesh files:

.. doctest::

   >>> mesh_file = '/path/to/mesh/file.obj'
   >>> sdk.datasets.upload_file(dataset=my_dataset.id,
   ...                          component='mesh',
   ...                          file_path=mesh_file)

   >>> first_texture = '/path/to/mesh/texture_a.jpg'
   >>> sdk.datasets.upload_file(dataset=my_dataset.id,
   ...                          component='texture_0',
   ...                          file_path=first_texture)

   >>> second_texture = '/path/to/mesh/texture_b.jpg'
   >>> sdk.datasets.upload_file(dataset=my_dataset.id,
   ...                          component='texture_1',
   ...                          file_path=second_texture)

   >>> material_file = '/path/to/mesh/material.mtl'
   >>> sdk.datasets.upload_file(dataset=my_dataset.id,
   ...                          component='material',
   ...                          file_path=material_file)

See the :py:class:`datasets.upload_file() <alteia.apis.client.datamngt.datasetsimpl.DatasetsImpl.upload_file>` documentation.documentation.

Create a raster dataset
------------------------

To create a ``raster`` dataset **with a world file and a projection file**:

.. doctest::

   >>> my_dataset = sdk.datasets.create_raster_dataset(name='My Raster',
   ...                                                 project=PROJECT_ID,
   ...                                                 mission=MISSION_ID,
   ...                                                 has_projection_file=True,
   ...                                                 has_worldfile=True)

See the :py:class:`datasets.create_raster_dataset() <alteia.apis.client.datamngt.datasetsimpl.DatasetsImpl.create_raster_dataset>` documentation.

And upload the raster files:

.. doctest::

   >>> raster_file = '/path/to/raster/file.tif'
   >>> sdk.datasets.upload_file(dataset=my_dataset.id,
   ...                          component='raster',
   ...                          file_path=raster_file)

   >>> world_file = '/path/to/raster/worldfile.tfw'
   >>> sdk.datasets.upload_file(dataset=my_dataset.id,
   ...                          component='worldfile',
   ...                          file_path=world_file)

   >>> projection_file = '/path/to/raster/projection.prj'
   >>> sdk.datasets.upload_file(dataset=my_dataset.id,
   ...                          component='projection',
   ...                          file_path=projection_file)

See the :py:class:`datasets.upload_file() <alteia.apis.client.datamngt.datasetsimpl.DatasetsImpl.upload_file>` documentation.documentation.

Create a file dataset
-----------------------------

To create a ``file`` dataset with several files:

.. doctest::

   >>> my_dataset = sdk.datasets.create_file_dataset(name='My File',
   ...                                               project=PROJECT_ID,
   ...                                               mission=MISSION_ID,
   ...                                               file_count=2)

See the :py:class:`datasets.create_file_dataset() <alteia.apis.client.datamngt.datasetsimpl.DatasetsImpl.create_file_dataset>` documentation.

And upload the dataset files:

.. doctest::

   >>> first_file = '/path/to/pcl/file.csv'
   >>> sdk.datasets.upload_file(dataset=my_dataset.id,
   ...                          component='file_0',
   ...                          file_path=first_file)

   >>> second_file = '/path/to/pcl/file.pdf'
   >>> sdk.datasets.upload_file(dataset=my_dataset.id,
   ...                          component='file_1',
   ...                          file_path=second_file)

See the :py:class:`datasets.upload_file() <alteia.apis.client.datamngt.datasetsimpl.DatasetsImpl.upload_file>` documentation.

Describe a dataset
-------------------

.. doctest::

   >>> my_dataset = sdk.datasets.describe(DATASET_ID)

See the :py:class:`datasets.describe() <alteia.apis.client.datamngt.datasetsimpl.DatasetsImpl.describe>` documentation.

Describe a list of datasets
----------------------------

.. doctest::

   >>> my_dataset_list = sdk.datasets.describe([DATASET_ID, ANOTHER_DATASET_ID])

See the :py:class:`datasets.describe() <alteia.apis.client.datamngt.datasetsimpl.DatasetsImpl.describe>` documentation.

Download a preview
-------------------

To download a preview of for a ``raster`` or ``image`` dataset:

.. doctest::

	>>> sdk.datasets.download_preview(dataset=DATASET_ID)

To download a small preview (instead of the default tiny one) of an ``image`` dataset:

.. doctest::

	>>> sdk.datasets.download_preview(dataset=DATASET_ID, kind='small')

See the :py:class:`datasets.download_preview() <alteia.apis.client.datamngt.datasetsimpl.DatasetsImpl.download_preview>` documentation.

Delete a dataset
-----------------

.. doctest::

   >>> sdk.datasets.delete(DATASET_ID)
   >>> sdk.datasets.delete([DATASET_ID1, DATASET_ID2])

See the :py:class:`datasets.delete() <alteia.apis.client.datamngt.datasetsimpl.DatasetsImpl.delete>` documentation.

With a list of datasets, all given IDs must be accessible to you to be able to perform the deletion. If only one
is not available to you, all the list will not be deleted. Warning with big list of datasets: the deletion will
perform multiple smaller requests, if a dataset is not accessible to you and is placed at the end of the list,
then all the first delete requests will be done, but not the last one.
