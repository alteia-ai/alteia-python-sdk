.. _dataflow:

Dataflow
========

Create a datastream template
----------------------------

.. doctest::

   >>> my_datastream_template = sdk.datastreamtemplates.create(
   ...     name = "My datastream template",
   ...     import_dataset = {
   ...         "dataset_parameters": {
   ...             "type": "pcl",
   ...             "categories": [],
   ...             "horizontal_srs_wkt": 'PROJCS["WGS 84 / UTM zone 31N",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",3],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","32631"]]',
   ...             "ingestion": {"parameters": {"compute_boundary": True}},
   ...         }
   ...     },
   ...     contextualisation = {
   ...         "type": "geographic",
   ...         "parameters": {
   ...             "assets_schema_repository": "My Asset Repository",
   ...             "geographic_buffer": 50,
   ...             "schemas": [
   ...                 {
   ...                     "assets_schema": "My_asset",
   ...                     "assets_schema_property_name": "My asset property",
   ...                     "geographic_buffer": 150,
   ...                 }
   ...             ],
   ...         },
   ...     },
   ...     source = {"type": "object-storage"},
   ...     transform = {
   ...         "analytic": {
   ...             "name": "pcl_segmentation",
   ...             "version_range": "3.0.x",
   ...             "inputs_mapping": {"input_pcl": "${import.output_dataset}"},
   ...             "parameters": {},
   ...             "outputs_mapping": "classified_pcl",
   ...         }
   ...     },
   ...     description = "description",
   ...     aggregate = {
   ...         "type": "pcl_aggregation",
   ...         "creation_parameters": {
   ...            "type": "pcl",
   ...            "categories": [
   ...            "classified"
   ...            ]
   ...         },
   ...         "ingestion_parameters": {
   ...            "tiling_profile": "potree2",
   ...            "compute_boundary": false,
   ...            "crop_on_extent": true
   ...         },
   ...         "strategy": {}
   ...      },
   ...     company = "507f191e810c19729de860eb",
   ... )

See the :py:class:`datastreamtemplates.create() <alteia.apis.client.datastreamtemplate.datastreamtemplateimpl.DatastreamTemplateImpl.create>` documentation.

Describe a datastream template
------------------------------

To describe a datastream template:

.. doctest::

   >>> my_datastream_template = sdk.datastreamtemplates.describe(template='5d1a14af0422ae12d537af02')

See the :py:class:`datastreamtemplates.describe() <alteia.apis.client.datastreamtemplate.datastreamtemplateimpl.DatastreamTemplateImpl.describe>` documentation.

Describes some datastream templates
-----------------------------------

To describe datastream templates:

.. doctest::

   >>> my_datastream_templates = sdk.datastreamtemplates.describes(templates=['5d1a14af0422ae12d537af02',
   ...                                      '5d1a14af0422ae12d537af05'])

See the :py:class:`datastreamtemplates.describes() <alteia.apis.client.datastreamtemplate.datastreamtemplateimpl.DatastreamTemplateImpl.describes>` documentation.

Create a datastream
-------------------

.. doctest::

   >>> my_datastream = sdk.datastreams.create(
   ...     name="My datastream",
   ...     start_date="2023-01-01T05:00:00.000Z",
   ...     end_date="2023-02-01T05:00:00.000Z",
   ...     source={
   ...         "url": "s3://myBucket/prefix/",
   ...         "regex": ".*las",
   ...         "synchronisation": {
   ...             "type": "on_trigger"
   ...             }
   ...          },
   ...     template="63b847191aa9840eaad2906a",
   ... )


See the :py:class:`datastreams.create() <alteia.apis.client.datastream.datastreamimpl.DatastreamImpl.create>` documentation.

Describe a datastream
---------------------

To describe a datastream:

.. doctest::

   >>> my_datastream = sdk.datastreams.describe(datastream='5d1a14af0422ae12d537af03')

See the :py:class:`datastreams.describe() <alteia.apis.client.datastream.datastreamimpl.DatastreamImpl.describe>` documentation.

Search datastream
-----------------

Search the first 20 datastream with `datastream` in the name, sort by newest first:

.. doctest::

   >>> my_filters = {'name': {'$match': 'datastream'}}
   >>> my_sort = {'creation_date': -1}
   >>> sdk.datastreams.search(filter=my_filters, sort=my_sort, limit=20)

Search the second page of same request:

.. doctest::

   >>> sdk.datastreams.search(filter=my_filters, sort=my_sort, limit=20, page=2)

See the :py:class:`datastreams.search() <alteia.apis.client.datastream.datastreamimpl.DatastreamImpl.search>` documentation.

Do some stuff for all results, without using pages but using iterator:

.. doctest::

   >>> ds = sdk.datastreams.search_generator(filter=my_filters, sort=my_sort)
   >>> for datastream in ds:
   ...     print(datastream.name)

See the :py:class:`datastreams.search_generator() <alteia.apis.client.datastream.datastreamimpl.DatastreamImpl.search_generator>` documentation.

Search datastream files
-----------------------

Search datastream files by datastream identifier sort by newest first:

.. doctest::

   >>> my_filters =  {"datastream": {"$eq":"6376535b507bcbec3b7b23b5"}}
   >>> my_sort = {'creation_date': -1}
   >>> sdk.datastreamsfiles.search(filter=my_filters, sort=my_sort)

See the :py:class:`datastreamsfiles.search() <alteia.apis.client.datastream.datastreamsfilesimpl.DatastreamsFilesImpl.search>` documentation.

Do some stuff for all results, without using pages but using iterator:

.. doctest::

   >>> dsf = sdk.datastreamsfiles.search_generator(filter=my_filters, sort=my_sort)
   >>> for datastream_file in dsf:
   ...     print(datastream_file.status)

See the :py:class:`datastreamsfiles.search_generator() <alteia.apis.client.datastream.datastreamsfilesimpl.DatastreamsFilesImpl.search_generator>` documentation.

Search datastream assets
------------------------

Search datastream assets by datastream identifier sort by newest first:

.. doctest::

   >>> my_filters =  {"datastream": {"$eq":"6376535b507bcbec3b7b23b5"}}
   >>> my_sort = {'creation_date': -1}
   >>> sdk.datastreamsassetsmonitored.search(filter=my_filters, sort=my_sort)

See the :py:class:`datastreamsassetsmonitored.search() <alteia.apis.client.datastream.datastreamassetmonitoredimpl.DatastreamsAssetMonitoredImpl.search>` documentation.

Do some stuff for all results, without using pages but using iterator:

.. doctest::

   >>> dsa = sdk.datastreamsassetsmonitored.search_generator(filter=my_filters, sort=my_sort)
   >>> for datastream_asset in dsa
   ...     print(datastream_asset.asset)

See the :py:class:`datastreamsassetsmonitored.search_generator() <alteia.apis.client.datastream.datastreamassetmonitoredimpl.DatastreamsAssetMonitoredImpl.search_generator>` documentation.

Delete a datastream
-------------------

To delete a datastream:

.. doctest::

   >>> my_datastream = sdk.datastreams.delete(datastream='5d1a14af0422ae12d537af03')

See the :py:class:`datastreams.delete() <alteia.apis.client.datastream.datastreamimpl.DatastreamImpl.delete>` documentation.
