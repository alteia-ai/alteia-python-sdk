<p align="center">
<img src="https://raw.githubusercontent.com/alteia-ai/alteia-python-sdk/master/docs/images/SDK_Python.png" alt="logo" style="max-width:100%;">

<p align="center">
<a href="https://pypi.org/project/alteia/" rel="nofollow"><img src="https://img.shields.io/pypi/v/alteia.svg" alt="pypi version" style="max-width:100%;"></a>
<a href="https://pypi.org/project/alteia/" rel="nofollow"><img src="https://img.shields.io/pypi/pyversions/alteia.svg" alt="compatible python versions" style="max-width:100%;"></a>
</p>

> This SDK offers a high-level Python interface to [Alteia APIs](https://www.alteia.com).

## Installation

```bash
pip install alteia
```

**requires Python >= 3.6.1*

## Basic usage

```python
import alteia

sdk = alteia.SDK(user="YOUR_EMAIL_ADDRESS", password="YOUR_ALTEIA_PASSWORD")

projects = sdk.projects.search(name="*")

for project in projects:
    print(project.name)

# My awesome project
```

<p>&nbsp;</p>

## 📕 Documentation

- [Reference documentation](https://alteia.readthedocs.io/en/latest/index.html)
- [Jupyter notebook tutorials](https://github.com/alteia-ai/tutorials)

## Contributing

Package installation:

```bash
poetry install
```

(Optional) To install pre-commit hooks (and detect problems before the pipelines):

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
pre-commit autoupdate  # Optional, to update pre-commit versions
```
