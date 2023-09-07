# -*- coding: utf-8 -*-

## Standard libraries
import os
import glob
import json
import logging
from typing import Union, List, Callable, Type

## Third-party libraries
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, validate_call
from pydantic_settings import BaseSettings

## Internal modules
from ._schema import BaseConfig
from ._utils import deep_merge
from .__version__ import __version__


logger = logging.getLogger(__name__)


class ConfigLoader:
    """A core class of `onion_config` module to use as the main config loader.

    Attributes:
        _ENV_FILE_PATH    (str     ): Default '.env' file path to load. Defaults to '${PWD}/.env'.
        _CONFIGS_DIR      (str     ): Default configs directory. Defaults to '${PWD}/configs'.
        _PRE_LOAD_HOOK    (function): Default lambda function for `pre_load_hook`. Defaults to `lambda config_data: config_data`.

        config            (Union[BaseConfig, BaseSettings, BaseModel]): Main config object (config_schema) for project. Defaults to None.
        config_schema     (Union[Type[BaseConfig], Type[BaseSettings], Type[BaseModel]]): Main config schema class to load and validate configs. Defaults to `BaseConfig`.
        config_data       (dict    ): Loaded data from config files as a dictionary. Defaults to {}.
        configs_dir       (str     ): Main configs directory to load all config files. Defaults to `ConfigLoader._CONFIGS_DIR`.
        extra_configs_dir (str     ): Extra configs directory to load extra config files. Defaults to None, but will use the 'ONION_CONFIG_EXTRA_DIR' environment variable if set.
        env_file_path     (str     ): '.env' file path to load. Defaults to `ConfigLoader._ENV_FILE_PATH`.
        required_envs     (str     ): Required environment variables to check. Defaults to [].
        pre_load_hook     (function): Custom pre-load method, this method will executed before validating `config`. Defaults to `ConfigLoader._PRE_LOAD_HOOK`.

    Methods:
        load()                    : Load and validate every configs into `config`.
        _load_dotenv()            : Loading environment variables from '.env' file, if it's exits.
        _check_required_envs()    : Check required environment variables are exist or not.
        _load_config_files()      : Load config files from `configs_dir` into `config_data`.
        _load_extra_config_files(): Load extra config files from `extra_configs_dir` into `config_data`.
    """

    _ENV_FILE_PATH = os.path.join(os.getcwd(), ".env")
    _CONFIGS_DIR = os.path.join(os.getcwd(), "configs")
    _PRE_LOAD_HOOK = lambda config_data: config_data

    @validate_call
    def __init__(
        self,
        configs_dir: str = _CONFIGS_DIR,
        config_schema: Union[
            Type[BaseConfig], Type[BaseSettings], Type[BaseModel]
        ] = BaseConfig,
        pre_load_hook: Callable = _PRE_LOAD_HOOK,
        env_file_path: str = _ENV_FILE_PATH,
        required_envs: List[str] = [],
        config_data: dict = {},
        extra_configs_dir: Union[str, None] = None,
        auto_load: bool = False,
    ):
        """ConfigLoader constructor method.

        Args:
            configs_dir       (str,      optional): Main configs directory to load all config files. Defaults to `ConfigLoader._CONFIGS_DIR`.
            config_schema     (Union[Type[BaseConfig], Type[BaseSettings], Type[BaseModel]], optional): Main config schema class to load and validate configs. Defaults to `BaseConfig`.
            pre_load_hook     (function, optional): Custom pre-load method, this method will executed before validating `config`. Defaults to `ConfigLoader._PRE_LOAD_HOOK`.
            env_file_path     (str,      optional): '.env' file path to load. Defaults to `ConfigLoader._ENV_FILE_PATH`.
            required_envs     (list,     optional): Required environment variables to check. Defaults to [].
            config_data       (dict,     optional): Custom config data to load before validating `config`. Defaults to {}.
            extra_configs_dir (str,      optional): Extra configs directory to load extra config files. Defaults to None.
            auto_load         (bool,     optional): Auto load configs on init or not. Defaults to False.
        """

        self.configs_dir = configs_dir
        self.config_schema = config_schema
        self.pre_load_hook = pre_load_hook
        self.env_file_path = env_file_path
        self.required_envs = required_envs
        self.config_data = config_data
        if extra_configs_dir:
            self.extra_configs_dir = extra_configs_dir

        if auto_load:
            self.load()

    def load(self) -> Union[BaseConfig, BaseSettings, BaseModel]:
        """Load and validate every configs into `config`.
        Load order:
            1. Load environment variables from '.env' file.
            2. Check required environment variables are exist or not.
            3. Load config files from `configs_dir` into `config_data`.
            4. Load extra config files from `extra_configs_dir` into `config_data`.
            5. Execute `pre_load_hook` method to modify `config_data`.
            6. Init `config_schema` with `config_data` into final `config`.

        Returns:
            Union[BaseConfig, BaseSettings, BaseModel]: Main config object (config_schema) for project.

        Raises:
            KeyError : If a required environment variable does not exist.
            Exception: If `pre_load_hook` or `config_schema` failed to execute.
        """

        self._load_dotenv()
        self._check_required_envs()
        self._load_config_files()
        self._load_extra_config_files()

        try:
            # 5. Execute `pre_load_hook` method:
            self.config_data: dict = self.pre_load_hook(self.config_data)
        except Exception:
            logger.critical("Failed to execute `pre_load_hook` method:")
            raise

        try:
            # 6. Init `config_schema` with `config_data`:
            self.config: Union[
                BaseConfig, BaseSettings, BaseModel
            ] = self.config_schema(**self.config_data)
        except Exception:
            logger.critical("Failed to init `config_schema`:")
            raise

        return self.config

    def _load_dotenv(self):
        """1. Loading environment variables from '.env' file, if it's exits."""

        if os.path.isfile(self.env_file_path):
            load_dotenv(dotenv_path=self.env_file_path, override=True, encoding="utf8")

    def _check_required_envs(self):
        """2. Check if required environment variables exist or not.

        If a required environment variable does not exist, an error is logged and raise an exception.

        Raises:
            KeyError: If a required environment variable does not exist.
        """

        for _env in self.required_envs:
            try:
                os.environ[_env]
            except KeyError:
                logger.critical(f"Missing required '{_env}' environment variable.")
                raise

    @validate_call
    def _load_config_files(self, configs_dir: Union[str, None] = None):
        """3. Load config files from `configs_dir` into `config_data`.

        Args:
            configs_dir (str, optional): Main configs directory to load all config files. Defaults to `ConfigLoader._CONFIGS_DIR`.

        Raises:
            Exception: If failed to load any config file.
        """

        _configs_dir = self.configs_dir
        if configs_dir:
            _configs_dir = configs_dir

        if os.path.isdir(_configs_dir):
            ## Loading all JSON config files from 'configs' directory:
            _json_file_paths = sorted(glob.glob(os.path.join(_configs_dir, "*.json")))
            for _json_file_path in _json_file_paths:
                try:
                    with open(_json_file_path, "r", encoding="utf8") as _json_file:
                        _new_config_dict = json.load(_json_file)
                        self.config_data = deep_merge(
                            self.config_data, _new_config_dict
                        )
                except Exception:
                    logger.critical(
                        f"Failed to load '{_json_file_path}' json config file:"
                    )
                    raise

            ## Loading all YAML config files from 'configs' directory:
            _yaml_file_paths = glob.glob(os.path.join(_configs_dir, "*.yml"))
            _yaml_file_paths.extend(glob.glob(os.path.join(_configs_dir, "*.yaml")))
            _yaml_file_paths.sort()
            for _yaml_file_path in _yaml_file_paths:
                try:
                    with open(_yaml_file_path, "r", encoding="utf8") as _yaml_file:
                        _new_config_dict = yaml.safe_load(_yaml_file)
                        self.config_data = deep_merge(
                            self.config_data, _new_config_dict
                        )
                except Exception:
                    logger.critical(
                        f"Failed to load '{_yaml_file_path}' yaml config file:"
                    )
                    raise

    def _load_extra_config_files(self):
        """4. Load extra config files from `extra_configs_dir` into `config_data`.

        Raises:
            Exception: If failed to load any extra config file.
        """

        if self.extra_configs_dir is None:
            _env_extra_configs_dir = os.getenv("ONION_CONFIG_EXTRA_DIR")
            if _env_extra_configs_dir:
                self.extra_configs_dir = _env_extra_configs_dir

        if self.extra_configs_dir:
            self._load_config_files(configs_dir=self.extra_configs_dir)

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

        self.__config_data = config_data

    ## config_data ##

    ## configs_dir ##
    @property
    def configs_dir(self) -> str:
        try:
            return self.__configs_dir
        except AttributeError:
            self.__configs_dir = ConfigLoader._CONFIGS_DIR

        return self.__configs_dir

    @configs_dir.setter
    def configs_dir(self, configs_dir: str):
        if not isinstance(configs_dir, str):
            raise TypeError(
                f"`configs_dir` attribute type {type(configs_dir)} is invalid, must be a <str>!"
            )

        configs_dir = configs_dir.strip()
        if configs_dir == "":
            raise ValueError("The `configs_dir` attribute value is empty!")

        self.__configs_dir = configs_dir

    ## configs_dir ##

    ## extra_configs_dir ##
    @property
    def extra_configs_dir(self) -> Union[str, None]:
        try:
            return self.__extra_configs_dir
        except AttributeError:
            return None

    @extra_configs_dir.setter
    def extra_configs_dir(self, extra_configs_dir: str):
        if not isinstance(extra_configs_dir, str):
            raise TypeError(
                f"`extra_configs_dir` attribute type {type(extra_configs_dir)} is invalid, must be a <str>!"
            )

        extra_configs_dir = extra_configs_dir.strip()
        if extra_configs_dir == "":
            raise ValueError("The `extra_configs_dir` attribute value is empty!")

        self.__extra_configs_dir = extra_configs_dir

    ## extra_configs_dir ##

    ## env_file_path ##
    @property
    def env_file_path(self) -> str:
        try:
            return self.__env_file_path
        except AttributeError:
            self.__env_file_path = ConfigLoader._ENV_FILE_PATH

        return self.__env_file_path

    @env_file_path.setter
    def env_file_path(self, env_file_path: str):
        if not isinstance(env_file_path, str):
            raise TypeError(
                f"The 'env_file_path' attribute type {type(env_file_path)} is invalid, must be a <str>!"
            )

        env_file_path = env_file_path.strip()
        if env_file_path == "":
            raise ValueError("The 'env_file_path' attribute value is empty!")

        self.__env_file_path = env_file_path

    ## env_file_path ##

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
                f"The 'required_envs' attribute type {type(required_envs)} is invalid, must be a <list>!"
            )

        if not all(isinstance(_val, str) for _val in required_envs):
            raise ValueError(
                f"The 'required_envs' attribute value {required_envs} is invalid, must be a list of <str>!"
            )

        self.__required_envs = required_envs

    ## required_envs ##

    ## pre_load_hook ##
    @property
    def pre_load_hook(self) -> Callable:
        try:
            return self.__pre_load
        except AttributeError:
            self.__pre_load = ConfigLoader._PRE_LOAD_HOOK

        return self.__pre_load

    @pre_load_hook.setter
    def pre_load_hook(self, pre_load_hook: Callable):
        if not callable(pre_load_hook):
            raise TypeError(
                f"`pre_load_hook` argument type {type(pre_load_hook)} is invalid, should be callable <function>!"
            )

        self.__pre_load = pre_load_hook

    ## pre_load_hook ##
    ### ATTRIBUTES ###
