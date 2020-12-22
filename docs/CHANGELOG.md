# Changelog

Notable changes to Alteia Python SDK are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2020-12-22

### Changed

- Remove dependency to requests-future (DAI-7241)
- Update client id and secret (DAI-7978)
- Do not require `name='*'` when searching for all the projects (DAI-7043)
- Simplify `Resource` class (DAI-7043)
- Several code modifications to improve readability and reduce abstractions (DAI-7043)
- Drop support of Python versions < 3.6.1 because they [officially reached the end of support deadlines](https://en.wikipedia.org/wiki/History_of_Python#Table_of_versions) (DAI-7043)
- Use poetry for dependency management (DAI-7043)
- Fix exception when using `utils.sanitize_dict` with Python 3.8 due to dict keys modified in loop on dict keys (DAI-6572)

### Added

- Support creation/description/deletion/search for carriers `sdk.carriers` (DAI-6933)
- Support creation/description/deletion/search/renaming and setting leader of teams `sdk.teams` (DAI-6933)
- Parameter to specify the access token `scope` at SDK instantiation (DAI-7805)
- Add `sdk.collection_tasks.create_flight_log` (DAI-7165)
- Support creation/deletion/search of data collection tasks `sdk.collection_tasks` (DAI-6863)
- Support creation/deletion/search of carrier models `sdk.carrier_models` (DAI-6863)
- Add pre-commit hooks for just-in-time code quality checks (DAI-7043)
- Add pylint and flake8 linting pipelines (DAI-7043)
- Common implementation of search generator for action based APIs (DAI-6925)

### Deleted

- Remove parameter to specify the `domain` at SDK instantiation, use `scope` (DAI-7805)
- Remove deprecated usage of `name` in `sdk.missions.search` (DAI-7043)
- Remove deprecated code in `sdk.annotations` (DAI-7043)
- Remove ResourceBaseManagers (DAI-7043)