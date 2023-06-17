# Documentation

## Pages

- [README](../README.md)
- [scripts](./scripts/README.md)

## ConfigLoader Class

The `ConfigLoader` class is the main class of the `onion_config` package. An instance of `ConfigLoader` represents a configuration loader that can load and validate configuration data from environment variables and config files.

### Properties

`ConfigLoader` instances have the following properties:

- **config**: Main config object for the project. It is an instance of a `BaseConfig`, `BaseSettings`, or `BaseModel` class, which holds the loaded and validated configuration data.
- **config_schema**: Main config schema class to load and validate configs. Defaults to `BaseConfig`.
- **config_data**: Loaded data from config files as a `python-box` Box. Defaults to `Box()`.
- **configs_dir**: Main configs directory to load all config files. Defaults to `'./configs'`.
- **extra_configs_dir**: Extra configs directory to load extra config files. Will use the `PY_EXTRA_CONFIGS_DIR` environment variable if set.
- **required_envs**: Required environment variables to check. Defaults to `[]`.
- **pre_load_hook**: Custom pre-load method, this method will be executed before loading and validating `config`. Defaults to a lambda function that simply returns its argument.

### Methods

`ConfigLoader` instances have the following methods:

- **load()**: Load and validate every config into `config`.
- **_load_dotenv()**: Loading environment variables from `.env` file, if it exists.
- **_check_required_envs()**: Check if required environment variables exist.
- **_load_config_files()**: Load config files from `configs_dir` into `config_data`.
- **_load_extra_config_files()**: Load extra config files from `extra_configs_dir` and update `config_data`.

## BaseConfig Class

The `BaseConfig` class is a subclass of `pydantic.BaseSettings` that is used as the default schema for validating configuration data in `onion_config`. It allows for arbitrary types and additional properties (extra).

It also overrides the `customise_sources` method to specify the order in which the configuration sources are checked. In `onion_config`, the environment variables are checked first, followed by the initial settings and then the file secret settings.
