# Documentation

## Pages

- [README](../README.md)
- [scripts](./scripts/README.md)

## ConfigLoader Class

The `ConfigLoader` class is the main class of the `onion_config` package. An instance of `ConfigLoader` represents a configuration loader that can load and validate configuration data from environment variables and config files.

### Properties

`ConfigLoader` instances have the following properties:

- **config**: Main config object (based on `config_schema`) for the project. It is an instance of a `BaseConfig`, `BaseSettings`, or `BaseModel` class, which holds the loaded and validated configuration data. Defaults to `BaseConfig`.
- **config_schema**: Main config schema class to load and validate configs. Defaults to `BaseConfig`.
- **config_data**: Loaded data from config files as a dictionary. Defaults to `{}`.
- **configs_dirs**: Main configs directories as list to load all config files. Defaults to `['./configs']`.
- **extra_dir**: Extra configs directory to load extra config files. Defaults to `None`, but will use the `ONION_CONFIG_EXTRA_DIR` environment variable if set.
- **env_file_paths**: Dotenv file paths as list to load. Defaults to `['.env']`.
- **required_envs**: Required environment variables to check. Defaults to `[]`.
- **pre_load_hook**: Custom pre-load method, this method will be executed before validating `config`. Defaults to `lambda config_data: config_data`.
- **quiet**: Quiet mode to suppress all warning logs. Defaults to `True`.

### Methods

`ConfigLoader` instances have the following methods:

- **load()**: 0. Load and validate every config into `config`.
- **_load_dotenv_files()**: 1. Load all dotenv files from `env_file_paths` into environment variables.
- **_load_dotenv_file()**: 1.1. Load each dotenv file into environment variables.
- **_check_required_envs()**: 2. Check if required environment variables exist.
- **_load_configs_dirs()**: 3. Load all config files from `configs_dirs` into `config_data`.
- **_load_configs_dir()**: 3.1. Load config files from each config directory into `config_data`.
- **_load_yaml_file()**: 3.1.a. Load each YAML config file into `config_data`.
- **_load_json_file()**: 3.1.b. Load each JSON config file into `config_data`.
- **_load_extra_dir()**: 4. Load extra config files from `extra_dir` into `config_data`.

### Load order

1. Load all dotenv files from `env_file_paths` into environment variables.
1.1. Load each dotenv file into environment variables.
2. Check if required environment variables exist or not.
3. Load all config files from `configs_dirs` into `config_data`.
3.1. Load config files from each config directory into `config_data`.
3.1.a. Load each YAML config file into `config_data`.
3.1.b. Load each JSON config file into `config_data`.
4. Load extra config files from `extra_dir` into `config_data`.
5. Execute `pre_load_hook` method to modify `config_data`.
6. Init `config_schema` with `config_data` into final `config`.

## BaseConfig Class

The `BaseConfig` class is a subclass of `pydantic_settings.BaseSettings` that is used as the default schema for validating configuration data in `onion_config`. It allows for arbitrary types and additional properties (extra).

It also overrides the `customise_sources` method to specify the order in which the configuration sources are checked. In `onion_config`, the dotenv files are checked first, environment variables are second, followed by the initial settings and then the file secret settings.
