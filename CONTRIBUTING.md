# How-to contribute to Alteia Python SDK

## Running unit tests

Unit tests are written with the `unittest` module (compatible with `pytest`):

```shell
$ python3 -m pip install -e .[tests]
$ python3 -m pip install -e .[coverage]
$ pytest --cov alteia --cov-report term --cov-report html
```

## Documentation

Building the documentation requires [pandoc](https://pandoc.org).

1. First install the dependencies:
   ```shell
   $ python3 -m pip install -e .[documentation]
   ```

2. Build the documentation:
   ```shell
   $ cd docs
   docs$ make html
   ```
   The generated documentation can be browsed opening the file
   `docs/_build/html/index.html` in a web browser.

3. (Optional) Automatic build while editing intensively the documentation
   ```shell
   docs$ python3 -m pip install sphinx-autobuild
   docs$ sphinx-autobuild docs _build/html
   ```
