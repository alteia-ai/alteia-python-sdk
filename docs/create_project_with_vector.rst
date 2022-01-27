.. _create_project_with_vector:

Create a project with a vector file
====================================

Let's create a project on Alteia, based on a vector file, such as a geojson file.

.. code-block:: python

  import logging
  import alteia

  logging.basicConfig(level=logging.DEBUG)

  sdk = alteia.SDK()

  # === Create the project ===

  company = sdk.companies.search()[0]
  my_project = sdk.projects.create(name="My project", company=company.id)

  # === Create the vector dataset and upload it ===

  vector_dataset = sdk.datasets.create_vector_dataset(
      name='My Vector',
      project=my_project.id,
      horizontal_srs_wkt='GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],TOWGS84[0,0,0,0,0,0,0],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]',
      dataset_format='geojson'
  )

  vector_file_to_upload = "/path/to/file.geojson"
  sdk.datasets.upload_file(
      dataset=vector_dataset.id,
      component='vector',
      file_path=vector_file_to_upload
  )

**The project is now available on Alteia 👍**
