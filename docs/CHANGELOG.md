# Changelog

Notable changes to Alteia Python SDK are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.7.0] - 2023-03-14

### Added
- Add `sdk.analytics.expose()` and `sdk.analytics.unexpose()` (DAI-16466)
- Add `sdk.analytics.enable()` and `sdk.analytics.disable()` instead (DAI-17814)

### Changed
- Deprecate `sdk.analytics.share_with_company()`, use `expose()` and `enable()` instead (DAI-16466, DAI-17814)
- Deprecate `sdk.analytics.unshare_with_company()`, use `unexpose()` or `disable()` instead (DAI-16466, DAI-17814)

### Deleted

## [2.6.0] - 2023-02-03

### Added
- Add `sdk.datastreams` with create/describe/search/search-generator/delete (DAI-17176)
- Add `sdk.datastreamsfiles` with search/search-generator (DAI-17176)
- Add `sdk.datastreamsassetsmonitored` with search/search-generator (DAI-17176)

### Changed

### Deleted

## [2.5.1] - 2022-10-25

### Added

- Add `sdk.datastreamtemplates` with create/describe/describes/search/delete/ (DAI-16691)
- Add `sdk.analytic_configurations` with create/describe/search/update/delete/assign/unassign (DAI-15894, DAI-17064)
- Change `external-provider-service` provider by `credentials-service` provider, the sdk will now use the credential service in order to store and interact with credential ressources (DAI-16717)

## [2.4.0] - 2022-09-27

### Added

- Add `features.remove_attachments()` (DAI-16196)
- Add `features.update_feature_properties()` (DAI-16106)
- Add `features.delete_feature_properties()` (DAI-16106)
- Add `features.delete_features_properties()` (DAI-16106)
- Add `geometry` to `missions.create_survey()` + update doc about `coordinates` (DAI-15520)

### Changed

- Change `features.update_features_properties()` return, now return a list of `Resource` (DAI-16106)

### Deleted

## [2.3.0] - 2022-06-20

### Added

- Add `collection_tasks.set_task_status` (DAI-15351)
- Add `pilots.describe` and `collection_tasks.describe` now accept a `fields` parameter to include or exclude fields from the response (DAI-15383)

## [2.2.0] - 2022-06-06

### Added
- Add `core.resources.datamngt.upload.cfg_multipart_upload()` (DAI-15147 DAI-15167)

## [2.1.0] - 2022-04-13

### Added
- Add `features.add_attachments()` (DAI-14397)

## [2.0.0] - 2022-02-02

### Changed
- Improve documentation readability (DAI-13485)
- Change the default UserAgent value by adding Python and OS versions. Now is like this: `alteia-sdk/x.x.x Python/x.x.x (Linux-x.x.x-x-amd64-x86_64)` (DAI-12882)
- Change signature `flights.describe()`: handle one or many IDs, and returns `Resource` or list of `Resource` (DAI-11598)
- Change signature `flights.search()`: new usage with `filter` parameter. Delete `project` and `mission` parameters (DAI-11598)
- Change signature `missions.describe()`: handle one or many IDs, and returns `Resource` or list of `Resource` (DAI-11598)
- Change signature `missions.search()`: new usage with `filter` parameter. Delete `missions`, `flights`, `project` and `deleted` parameters (DAI-11598)
- Change signature `projects.describe()`: handle one or many IDs, and returns `Resource` or list of `Resource` (DAI-11598)
- Change signature `projects.search()`: new usage with `filter` parameter. Delete `name` and `deleted` parameters (DAI-11598)
- Improve all `describe()` methods when using a very big list of IDs (DAI-13548)
- Improve all `delete()` methods when using a very big list of IDs (DAI-13607)
- Initialization of `Resource` do not remove fields equals to `None` by default.

### Added
- Add argument `kind` for `datasets.download_preview()`, allowing to download small previews, not only tiny (DAI-13014)
- Add `AbstractConnection.set_user_agent()`: allow to add multiples information to UserAgent request's headers (DAI-12882)
- New argument `service` for SDK init, to add a service name in UserAgent (DAI-12882)
- Upload big file: fix chunk size calculation if more than 10000 parts (DAI-12669)
- Add `utils.human_bytes()` to display bytes as human readable (DAI-12669)
- Add `fields` parameter in `utils.search()` and `utils.search_generator()`
- Add `flights.describe_uploads_status()` (DAI-11598)
- Add `flights.search_generator()` (DAI-11598)
- Add `flights.update_name()` (DAI-11598)
- Add `flights.update_survey_date()` (DAI-11598)
- Add `flights.update_geodata()` (DAI-11598)
- Add `flights.update_bbox()` (DAI-11598)
- Add `flights.update_status()` (DAI-11598)
- Add `missions.search_generator()` (DAI-11598)
- Add `missions.update_name()` (DAI-11598)
- Add `missions.update_survey_date()` (DAI-11598)
- Add `missions.update_geometry()` (DAI-11598)
- Add `missions.update_bbox()` (DAI-11598)
- Add `missions.compute_bbox()` (DAI-11598)
- Add `missions.create_archive()` (DAI-11598)
- Add `projects.search_generator()` (DAI-11598)
- Add `projects.update_name()` (DAI-11598)
- Add `projects.update_geometry()` (DAI-11598)
- Add `projects.update_bbox()` (DAI-11598)
- Add `projects.compute_bbox()` (DAI-11598)
- Add `projects.update_units()` (DAI-11598)
- Add `projects.update_srs()` (DAI-11598)
- Add `projects.update_local_coordinates_dataset()` (DAI-11598)
- Add `projects.update_location()` (DAI-11598)
- Add "How to upgrade" section in the documentation (DAI-13510)

### Deleted
- Remove legacy `secret` argument in SDK init. Use `client_secret` instead.
- Remove legacy `company` argument in `share_tokens.search()`. Use `filter` instead.
- Replaced `UIServicesAPI` by a new `ProjectManagerAPI` (DAI-11598)
- Delete `missions.complete_survey_upload()`: use `flights.update_status()` instead (DAI-11598)
- Delete `missions.rename()`: use `missions.update_name()` instead (DAI-11598)
- Delete `projects.rename()`: use `projects.update_name()` instead (DAI-11598)

## [1.3.7] - 2022-01-26

### Changed

- Fix bug in `sdk.datasets.share_tiles` function when sharing tiles for several datasets (DAI-13735)
- Display a warning or raise an exception if too many datasets are requested in `sdk.datasets.share_tiles` (DAI-13735)

## [1.3.6] - 2022-01-13

### Changed

- Use "importlib" instead of "pkg_resources" to retrieve WKT strings (DAI-13330)
- Fix failure to parse some timestamps while retrieving products logs
  (DAI-13266)

## [1.3.5] - 2021-12-07

### Changed

- Instantiating `SDK` using the `secret` argument is deprecated, use
  the `client_secret` argument (DAI-12191)

- Increase timeout for upload multipart requests (DAI-13066)

- Increase timeout for API requests from 30s to 600s (10 min) (DAI-12673)

### Added

- New manager `sdk.oauth_clients` to manage OAuth clients (DAI-12191)

- New `sdk.features` and `sdk.collections` resource managers
  (DAI-13206)

- Allow `sdk.analytics.order()` to order an analytic by name and
  version (DAI-13133)

- New `sdk.analytics.describe_by_name()` to describe an analytic by
  name and version (DAI-13133)

- Method to revoke a token on `TokenManager` class (DAI-13004)

- Support `sort` parameter in `sdk.*.search_generator` (DAI-12813)

### Deleted

- Support for specifying OAuth client secret in configuration file
  under the `secret` key has been removed, use `client_secret`
  (DAI-12191)

## [1.3.4] - 2021-11-09

### Changed

- Do not pass unset parameters for the dataset creation (DAI-12690)

## [1.3.3] - 2021-10-20

### Changed

- Fix mypy errors (DAI-4205)
- Convert all formatted strings to the f-string syntax (DAI-12253)

## [1.3.2] - 2021-09-22

### Changed

- Use new logo (DAI-11977)
- Use type aliases instead of `NewType` in `alteia.core.utils.typing` (DAI-11769)
- Add missing JSON serialization in `describe_token()` (DAI-11767)

### Added

- Add an option `force_prompt` to ask the user to confirm or modify his credentials when instantiating the `SDK` (DAI-12083)

## [1.3.1] - 2021-08-09

### Changed

- Set minimum version of `urllib3` to 1.26, to fix `unexpected keyword argument 'allowed_methods'` error (DAI-11501)

## [1.3.0] - 2021-07-28

### Changed

- `sdk.datasets.share_tiles()` now supports creating tile URL for multiple raster datasets (DAI-11058)
- Harmonize `sdk.share_tokens.create()` and `sdk.share_tokens.search()` instance of `Resource` class (DAI-10818)
- Deprecates `company` argument of `sdk.share_tokens.search()` (DAI-10818)
- Use `allowed_methods` instead of `method_whitelist` to remove deprecation warning when instantiating SDK (DAI-11056)
- `sdk.share_tokens.create()` now support creating share tokens for multiple datasets (DAI-10782)
- `sdk.share_tokens.search()` now support usual API search syntax (DAI-10818)

## [1.2.1] - 2021-06-23

### Changed

- Fix crash in `products.retrieve_logs` if the log timestamps does not contain enough digits for microseconds (DAI-10960)

## [1.2.0] - 2021-06-15

### Changed

- `company` is now required when creating a project with `sdk.projects.create()` (DAI-10595)

### Added

- Add missing API reference in the documentation (DAI-10294)
- Add type hints for every resource implementation (DAI-10041)
- Add `py.typed` to the package to benefit from mypy type hints (DAI-10041)
- Add 5 new arrow icons in Icons enum (DAI-10680)

## [1.1.0] - 2021-05-17

### Changed

- Share token actions don't use current company anymore (DAI-9417)
- `project` or `company` required to create a dataset (DAI-9679)
- `company` required to create an analytic (DAI-8800)
- `version` required to create an analytic (DAI-9746)

### Added

- Add `sdk._connection._token_manager.describe_token()` to describe an access token (DAI-10281)
- Add `sdk.companies` and `sdk.users` to search or describe user and companies (DAI-10281)
- Add `timeout` parameter in providers for get/post/put/delete methods (DAI-10100)

## [1.0.4] - 2021-03-31

### Added

- Add `keyset_pagination` option in search generator to optimize searches (DAI-8987)

## [1.0.3] - 2021-03-30

### Changed

- Sort logs chronologically in `products.retrieve_logs` to avoid duplicated log entries in `products.follow_logs` (DAI-9522)
- Sort by `_id` in `search_generator` as `creation_date` may be missing sometimes (DAI-9144)

### Added

- Add `sdk.collection_tasks.update` to update a collection task (DAI-9381)
- Add `sdk.collection_tasks.rename` to rename a collection task (DAI-8021)
- Add `sdk.projects.rename` to rename a project (DAI-8021)
- Add `sdk.collection_tasks.search_generator` (DAI-9144)

## [1.0.2] - 2021-02-10

### Changed

- Fix `sdk.flights.describe` function (DAI-8446)

### Added

- Ability to rename a mission (DAI-8462)
- Add search generator in `sdk.annotations` (DAI-8446)
- Add share/unshare an analytic with a company: `sdk.analytics.share`, `sdk.analytics.unshare` (DAI-8746)

## [1.0.1] - 2020-12-29

### Added

- Add generic search function in `alteia/core/resources` (DAI-8219)
- Add the base url as referear in each request headers (DAI-8283)

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
