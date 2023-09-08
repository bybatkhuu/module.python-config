# -*- coding: utf-8 -*-

## Standard libraries
import os
import glob
import json
import copy
import logging
from typing import Union, List, Callable, Type

## Third-party libraries
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, validate_call
from pydantic_settings import BaseSettings

## Internal modules
from ._utils import deep_merge
from ._schema import BaseConfig
from .__version__ import __version__


logger = logging.getLogger(__name__)


class ConfigLoader:
    """A core class of `onion_config` module to use as the main config loader.

    Attributes:
        _ENV_FILE_PATH (str                       ): Default dotenv file path to load. Defaults to '${PWD}/.env'.
        _CONFIGS_DIR   (str                       ): Default configs directory. Defaults to '${PWD}/configs'.
        _PRE_LOAD_HOOK (function                  ): Default lambda function for `pre_load_hook`. Defaults to `lambda config_data: config_data`.

        config         (Union[BaseConfig,
                              BaseSettings,
                              BaseModel          ]): Main config object (based on `config_schema`) for project. Defaults to None.
        config_schema  (Union[Type[BaseConfig],
                              Type[BaseSettings],
                              Type[BaseModel]    ]): Main config schema class to load and validate configs. Defaults to `BaseConfig`.
        config_data    (dict                      ): Loaded data from config files as a dictionary. Defaults to {}.
        configs_dirs   (str                       ): Main configs directories as <list> to load all config files. Defaults to [ConfigLoader._CONFIGS_DIR].
        extra_dir      (str                       ): Extra configs directory to load extra config files. Defaults to None, but will use the 'ONION_CONFIG_EXTRA_DIR' environment variable if set.
        env_file_paths (str                       ): Dotenv file paths as <list> to load. Defaults to [ConfigLoader._ENV_FILE_PATH].
        required_envs  (str                       ): Required environment variables to check. Defaults to [].
        pre_load_hook  (function                  ): Custom pre-load method, this method will executed before validating `config`. Defaults to `ConfigLoader._PRE_LOAD_HOOK`.
        quiet          (bool                      ): If False, will show warning messages. Defaults to True.

    Methods:
        load()                : Load and validate every configs into `config`.
        _load_dotenv_files()  : Load all dotenv files from `env_file_paths` into environment variables.
        _load_dotenv_file()   : Load each dotenv file into environment variables.
        _check_required_envs(): Check required environment variables are exist or not.
        _load_configs_dirs()  : Load all config files from `configs_dirs` into `config_data`.
        _load_configs_dir()   : Load config files from each config directory into `config_data`.
        _load_yaml_file()     : Load each YAML config file into `config_data`.
        _load_json_file()     : Load each JSON config file into `config_data`.
        _load_extra_dir()     : Load extra config files from `extra_dir` into `config_data`.
    """

    _ENV_FILE_PATH = os.path.join(os.getcwd(), ".env")
    _CONFIGS_DIR = os.path.join(os.getcwd(), "configs")
    _PRE_LOAD_HOOK = lambda config_data: config_data

    @validate_call
    def __init__(
        self,
        config_schema: Union[
            Type[BaseConfig], Type[BaseSettings], Type[BaseModel]
        ] = BaseConfig,
        configs_dirs: Union[List[str], str] = _CONFIGS_DIR,
        env_file_paths: Union[List[str], str] = _ENV_FILE_PATH,
        required_envs: List[str] = [],
        pre_load_hook: Callable = _PRE_LOAD_HOOK,
        extra_dir: Union[str, None] = None,
        config_data: dict = {},
        quiet: bool = True,
        auto_load: bool = False,
    ):
        """ConfigLoader constructor method.

        Args:
            config_schema  (Union[Type[BaseConfig],
                                  Type[BaseSettings],
                                  Type[BaseModel]]  , optional): Main config schema class to load and validate configs. Defaults to `BaseConfig`.
            configs_dirs   (Union[List[str], str]   , optional): Main configs directories as <list> or <str> to load all config files. Defaults to `ConfigLoader._CONFIGS_DIR`.
            env_file_paths (Union[List[str], str]   , optional): Dotenv file paths as <list> or <str> to load. Defaults to `ConfigLoader._ENV_FILE_PATH`.
            required_envs  (List[str]               , optional): Required environment variables to check. Defaults to [].
            pre_load_hook  (function                , optional): Custom pre-load method, this method will executed before validating `config`. Defaults to `ConfigLoader._PRE_LOAD_HOOK`.
            extra_dir      (Union[str, None]        , optional): Extra configs directory to load extra config files. Defaults to None.
            config_data    (dict                    , optional): Base config data as <dict> before everything. Defaults to {}.
            quiet          (bool                    , optional): If False, will show warning messages. Defaults to True.
            auto_load      (bool                    , optional): Auto load configs on init or not. Defaults to False.
        """

        self.config_schema = config_schema
        self.configs_dirs = configs_dirs
        self.env_file_paths = env_file_paths
        self.required_envs = required_envs
        self.pre_load_hook = pre_load_hook
        if extra_dir:
            self.extra_dir = extra_dir
        self.config_data = config_data
        self.quiet = quiet

        if auto_load:
            self.load()

    @validate_call
    def load(self) -> Union[BaseConfig, BaseSettings, BaseModel]:
        """Load and validate every configs into `config`.
        Load order:
            1.     Load all dotenv files from `env_file_paths` into environment variables.
            1.1.   Load each dotenv file into environment variables.
            2.     Check if required environment variables exist or not.
            3.     Load all config files from `configs_dirs` into `config_data`.
            3.1.   Load config files from each config directory into `config_data`.
            3.1.a. Load each YAML config file into `config_data`.
            3.1.b. Load each JSON config file into `config_data`.
            4.     Load extra config files from `extra_dir` into `config_data`.
            5.     Execute `pre_load_hook` method to modify `config_data`.
            6.     Init `config_schema` with `config_data` into final `config`.

        Raises:
            Exception: If `pre_load_hook` method failed to execute.
            Exception: If `config_schema` failed to init.

        Returns:
            Union[BaseConfig, BaseSettings, BaseModel]: Main config object (based on `config_schema`) for project.
        """

        self._load_dotenv_files()
        self._check_required_envs()
        self._load_configs_dirs()
        self._load_extra_dir()

        try:
            # 5. Execute `pre_load_hook` method to modify `config_data`:
            self.config_data: dict = self.pre_load_hook(self.config_data)
        except Exception:
            logger.critical("Failed to execute `pre_load_hook` method:")
            raise

        try:
            # 6. Init `config_schema` with `config_data` into final `config`:
            self.config: Union[
                BaseConfig, BaseSettings, BaseModel
            ] = self.config_schema(**self.config_data)
        except Exception:
            logger.critical("Failed to init `config_schema`:")
            raise

        return self.config

    def _load_dotenv_files(self):
        """1. Load all dotenv files from `env_file_paths` into environment variables."""

        for _env_file_path in self.env_file_paths:
            self._load_dotenv_file(env_file_path=_env_file_path)

    @validate_call
    def _load_dotenv_file(self, env_file_path: str):
        """1.1. Load each dotenv file into environment variables.

        Args:
            env_file_path (str, required): Dotenv file path to load.
        """

        if not os.path.isabs(env_file_path):
            env_file_path = os.path.join(os.getcwd(), env_file_path)

        if os.path.isfile(env_file_path):
            load_dotenv(dotenv_path=env_file_path, override=True, encoding="utf8")
        else:
            if self.quiet:
                logger.debug(f"'{env_file_path}' file is not exist!")
            else:
                logger.warning(f"'{env_file_path}' file is not exist!")

    def _check_required_envs(self):
        """2. Check if required environment variables exist or not.
        If a required environment variable does not exist, raise an exception.

        Raises:
            KeyError: If a required environment variable does not exist.
        """

        for _env in self.required_envs:
            try:
                os.environ[_env]
            except KeyError:
                logger.critical(f"Missing required '{_env}' environment variable.")
                raise

    def _load_configs_dirs(self):
        """3. Load all config files from `configs_dirs` into `config_data`."""

        for _config_dir in self.configs_dirs:
            self._load_configs_dir(configs_dir=_config_dir)

    @validate_call
    def _load_configs_dir(self, configs_dir: str):
        """3.1. Load config files from each config directory into `config_data`.

        Args:
            configs_dir (str, required): Configs directory to load.
        """

        if not os.path.isabs(configs_dir):
            configs_dir = os.path.join(os.getcwd(), configs_dir)

        if os.path.isdir(configs_dir):
            _file_paths = []
            _file_paths.extend(glob.glob(os.path.join(configs_dir, "*.yaml")))
            _file_paths.extend(glob.glob(os.path.join(configs_dir, "*.yml")))
            _file_paths.extend(glob.glob(os.path.join(configs_dir, "*.json")))
            # _file_paths.extend(glob.glob(os.path.join(configs_dir, "*.toml")))
            _file_paths.sort()

            for _file_path in _file_paths:
                if _file_path.lower().endswith((".yml", ".yaml")):
                    self._load_yaml_file(file_path=_file_path)
                elif _file_path.lower().endswith(".json"):
                    self._load_json_file(file_path=_file_path)
                # elif _file_path.lower().endswith(".toml"):
                #     self._load_toml_file(file_path=_file_path)
        else:
            if self.quiet:
                logger.debug(f"'{configs_dir}' directory is not exist!")
            else:
                logger.warning(f"'{configs_dir}' directory is not exist!")

    @validate_call
    def _load_yaml_file(self, file_path: str):
        """3.1.a. Load each YAML config file into `config_data`.

        Args:
            file_path (str, required): YAML config file path to load.

        Raises:
            Exception: If failed to load any YAML config file.
        """

        if os.path.isfile(file_path):
            try:
                with open(file_path, "r", encoding="utf8") as _file:
                    _new_config_dict = yaml.safe_load(_file) or {}
                    self.config_data = deep_merge(self.config_data, _new_config_dict)
            except Exception:
                logger.critical(f"Failed to load '{file_path}' YAML config file:")
                raise
        else:
            if not self.quiet:
                logger.warning(f"'{file_path}' YAML config file is not exist!")

    @validate_call
    def _load_json_file(self, file_path: str):
        """3.1.b. Load each JSON config file into `config_data`.

        Args:
            file_path (str, required): JSON config file path to load.

        Raises:
            Exception: If failed to load any JSON config file.
        """

        if os.path.isfile(file_path):
            try:
                with open(file_path, "r", encoding="utf8") as _file:
                    _new_config_dict = json.load(_file) or {}
                    self.config_data = deep_merge(self.config_data, _new_config_dict)
            except Exception:
                logger.critical(f"Failed to load '{file_path}' JSON config file:")
                raise
        else:
            if not self.quiet:
                logger.warning(f"'{file_path}' JSON config file is not exist!")

    # @validate_call
    # def _load_toml_file(self, file_path: str):
    #     """3.1.c. Load each TOML config file into `config_data`.

    #     Args:
    #         file_path (str, required): TOML config file path to load.

    #     Raises:
    #         Exception: If failed to load any TOML config file.
    #     """

    #     if os.path.isfile(file_path):
    #         try:
    #             import toml

    #             with open(file_path, "r", encoding="utf8") as _file:
    #                 _new_config_dict = toml.load(_file) or {}
    #                 self.config_data = deep_merge(self.config_data, _new_config_dict)
    #         except Exception:
    #             logger.critical(f"Failed to load '{file_path}' TOML config file:")
    #             raise
    #     else:
    #         if not self.quiet:
    #             logger.warning(f"'{file_path}' TOML config file is not exist!")

    def _load_extra_dir(self):
        """4. Load extra config files from `extra_dir` into `config_data`."""

        _env_extra_dir = os.getenv("ONION_CONFIG_EXTRA_DIR")
        if _env_extra_dir:
            self.extra_dir = _env_extra_dir

        if self.extra_dir:
            self._load_configs_dir(configs_dir=self.extra_dir)

    ### ATTRIBUTES ###

    ## config ##
    @property
    def config(self) -> Union[BaseConfig, BaseSettings, BaseModel, None]:
        try:
            return self.__config
        except AttributeError:
            return None

    @config.setter
    def config(self, config: Union[BaseConfig, BaseSettings, BaseModel]):
        if (
            (not isinstance(config, BaseConfig))
            and (not isinstance(config, BaseSettings))
            and (not isinstance(config, BaseModel))
        ):
            raise TypeError(
                f"`config` attribute type {type(config)} is invalid, must be a <class 'BaseConfig'> or `pydantic` <class 'BaseSettings'> or <class 'BaseModel'>."
            )

        self.__config = config

    ## config ##

    ## config_schema ##
    @property
    def config_schema(
        self,
    ) -> Union[Type[BaseConfig], Type[BaseSettings], Type[BaseModel]]:
        try:
            return self.__config_schema
        except AttributeError:
            self.__config_schema = BaseConfig

        return self.__config_schema

    @config_schema.setter
    def config_schema(
        self,
        config_schema: Union[Type[BaseConfig], Type[BaseSettings], Type[BaseModel]],
    ):
        # Check if config_schema is a class (i.e., an instance of type)
        if not isinstance(config_schema, type):
            raise TypeError("`config_schema` must be a class, not an instance.")

        # Check if config_schema is a subclass of BaseConfig, BaseSettings or BaseModel
        if (
            (not issubclass(config_schema, BaseConfig))
            and (not issubclass(config_schema, BaseSettings))
            and (not issubclass(config_schema, BaseModel))
        ):
            _base_class = ""
            if hasattr(config_schema, "__base__"):
                _base_class = config_schema.__base__
            else:
                _base_class = type(config_schema)

            raise TypeError(
                f"`config_schema` attribute base class {_base_class} is invalid, must be a Type[<class 'BaseConfig'>] or `pydantic` Type[<class 'BaseSettings'>, <class 'BaseModel'>]."
            )

        self.__config_schema = config_schema

    ## config_schema ##

    ## config_data ##
    @property
    def config_data(self) -> dict:
        try:
            return self.__config_data
        except AttributeError:
            self.__config_data = {}

        return self.__config_data

    @config_data.setter
    def config_data(self, config_data: dict):
        if not isinstance(config_data, dict):
            raise TypeError(
                f"`config_data` attribute type {type(config_data)} is invalid, must be a <dict>."
            )

        self.__config_data = copy.deepcopy(config_data)

    ## config_data ##

    ## configs_dirs ##
    @property
    def configs_dirs(self) -> List[str]:
        try:
            return self.__configs_dirs
        except AttributeError:
            self.__configs_dirs = [ConfigLoader._CONFIGS_DIR]

        return self.__configs_dirs

    @configs_dirs.setter
    def configs_dirs(self, configs_dirs: Union[List[str], str]):
        if (not isinstance(configs_dirs, str)) and (not isinstance(configs_dirs, list)):
            raise TypeError(
                f"`configs_dirs` attribute type {type(configs_dirs)} is invalid, must be a <list> or <str>!"
            )

        if isinstance(configs_dirs, str):
            configs_dirs = configs_dirs.strip()
            if configs_dirs == "":
                raise ValueError("The `configs_dirs` attribute value is empty!")

            configs_dirs = [configs_dirs]
        else:
            configs_dirs = copy.deepcopy(configs_dirs)

        if not all(isinstance(_val, str) for _val in configs_dirs):
            raise ValueError(
                f"'configs_dirs' attribute value {configs_dirs} is invalid, must be a list of <str>!"
            )

        self.__configs_dirs = configs_dirs

    ## configs_dirs ##

    ## extra_dir ##
    @property
    def extra_dir(self) -> Union[str, None]:
        try:
            return self.__extra_dir
        except AttributeError:
            return None

    @extra_dir.setter
    def extra_dir(self, extra_dir: str):
        if not isinstance(extra_dir, str):
            raise TypeError(
                f"`extra_dir` attribute type {type(extra_dir)} is invalid, must be a <str>!"
            )

        extra_dir = extra_dir.strip()
        if extra_dir == "":
            raise ValueError("The `extra_dir` attribute value is empty!")

        self.__extra_dir = extra_dir

    ## extra_dir ##

    ## env_file_paths ##
    @property
    def env_file_paths(self) -> List[str]:
        try:
            return self.__env_file_paths
        except AttributeError:
            self.__env_file_paths = [ConfigLoader._ENV_FILE_PATH]

        return self.__env_file_paths

    @env_file_paths.setter
    def env_file_paths(self, env_file_paths: Union[List[str], str]):
        if (not isinstance(env_file_paths, str)) and (
            not isinstance(env_file_paths, list)
        ):
            raise TypeError(
                f"'env_file_paths' attribute type {type(env_file_paths)} is invalid, must be a <list> or <str>!"
            )

        if isinstance(env_file_paths, str):
            env_file_paths = env_file_paths.strip()
            if env_file_paths == "":
                raise ValueError("The `env_file_paths` attribute value is empty!")

            env_file_paths = [env_file_paths]
        else:
            env_file_paths = copy.deepcopy(env_file_paths)

        if not all(isinstance(_val, str) for _val in env_file_paths):
            raise ValueError(
                f"'env_file_paths' attribute value {env_file_paths} is invalid, must be a list of <str>!"
            )

        self.__env_file_paths = env_file_paths

    ## env_file_paths ##

    ## required_envs ##
    @property
    def required_envs(self) -> List[str]:
        try:
            return self.__required_envs
        except AttributeError:
            self.__required_envs = []

        return self.__required_envs

    @required_envs.setter
    def required_envs(self, required_envs: List[str]):
        if not isinstance(required_envs, list):
            raise TypeError(
                f"'required_envs' attribute type {type(required_envs)} is invalid, must be a <list>!"
            )

        if not all(isinstance(_val, str) for _val in required_envs):
            raise ValueError(
                f"'required_envs' attribute value {required_envs} is invalid, must be a list of <str>!"
            )

        self.__required_envs = copy.deepcopy(required_envs)

    ## required_envs ##

    ## pre_load_hook ##
    @property
    def pre_load_hook(self) -> Callable:
        try:
            return self.__pre_load_hook
        except AttributeError:
            self.__pre_load_hook = ConfigLoader._PRE_LOAD_HOOK

        return self.__pre_load_hook

    @pre_load_hook.setter
    def pre_load_hook(self, pre_load_hook: Callable):
        if not callable(pre_load_hook):
            raise TypeError(
                f"`pre_load_hook` argument type {type(pre_load_hook)} is invalid, should be callable <function>!"
            )

        self.__pre_load_hook = pre_load_hook

    ## pre_load_hook ##

    ## quiet ##
    @property
    def quiet(self) -> bool:
        try:
            return self.__quiet
        except AttributeError:
            return True

    @quiet.setter
    def quiet(self, quiet: bool):
        if not isinstance(quiet, bool):
            raise TypeError(
                f"'quiet' attribute type {type(quiet)} is invalid, must be a <bool>!"
            )

        self.__quiet = quiet

    ## quiet ##
    ### ATTRIBUTES ###
