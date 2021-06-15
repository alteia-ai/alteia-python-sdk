.. _create_project_with_images:

Create a project with images
=============================

Let's create a project on Alteia, and upload images on it:

.. code-block:: python

  import logging
  import alteia

  logging.basicConfig(level=logging.DEBUG)

  sdk = alteia.SDK()

  # === Create the project ===

  company = sdk.companies.search()[0]
  my_project = sdk.projects.create(name="My project", company=company.id)

  # === Create the survey (mission + flight) with 2 images ===

  my_flight, my_mission = sdk.missions.create(
    name='My survey',
    coordinates=[[LONGITUDE1, LATITUDE1],[LONGITUDE2,LATITUDE2], ...],
    project=my_project.id,
    survey_date='2019-01-01T00:00:00.000Z',
    number_of_images=2)

  # === Create the dataset for the image 1 and upload it ===

  image1_dataset = sdk.datasets.create_image_dataset(
    name='Image 1',
    project=my_project.id,
    mission=my_mission.id,
    flight=my_flight.id,
    geometry={'type': 'Point', 'coordinates': [IMG1_LONGITUDE, IMG1_LATITUDE]},
    width=IMAGE_WIDTH_IN_PIXELS,
    height=IMAGE_HEIGHT_IN_PIXELS,
    )

  image1_path = '/path/to/image1.jpg'
  sdk.datasets.upload_file(
    dataset=image1_dataset.id,
    component='image',
    file_path=image1_path)

  # === Create the dataset for the image 2 and upload it ===

  image2_dataset = sdk.datasets.create_image_dataset(
    name='Image 2',
    project=my_project.id,
    mission=my_mission.id,
    flight=my_flight.id,
    geometry={'type': 'Point', 'coordinates': [IMG2_LONGITUDE, IMG2_LATITUDE]},
    width=IMAGE_WIDTH_IN_PIXELS,
    height=IMAGE_HEIGHT_IN_PIXELS,
    )

  image2_path = '/path/to/image2.jpg'
  sdk.datasets.upload_file(
    dataset=image2_dataset.id,
    component='image',
    file_path=image2_path)

  # === Complete the survey upload ===

  sdk.missions.complete_survey_upload(flight=my_flight.id)

**The project, along with the mission and its images are now available on Alteia 👍**
