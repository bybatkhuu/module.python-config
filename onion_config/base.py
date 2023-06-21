# -*- coding: utf-8 -*-

import os
import glob
import json
import logging
from typing import Union, List, Callable, TypeVar

import yaml
from box import Box
from dotenv import load_dotenv
from pydantic import BaseSettings, BaseModel, validate_arguments
from pydantic.env_settings import SettingsSourceCallable

from .__version__ import __version__


logger = logging.getLogger(__name__)


class BaseConfig(BaseSettings):
    class Config:
        extra = "allow"
        frozen = True
        arbitrary_types_allowed = True

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> tuple[SettingsSourceCallable, ...]:
            return env_settings, init_settings, file_secret_settings


_ConfigType = TypeVar("_ConfigType", bound=Union[BaseConfig, BaseSettings, BaseModel])


class ConfigLoader:
    """A core class of 'onion_config' module to use as the main config loader.

    Attributes:
        _ENV_FILE_PATH    (str     ): Default '.env' file path to load. Defaults to '${PWD}/.env'.
        _CONFIGS_DIR      (str     ): Default configs directory. Defaults to '${PWD}/configs'.
        _PRE_LOAD_HOOK    (function): Default lambda function for 'pre_load_hook'. Defaults to <lambda config_data: config_data>.

        config            (Union[BaseConfig, BaseSettings, BaseModel]): Main config object (config_schema) for project. Defaults to None.
        config_schema     (_ConfigType): Main config schema class to load and validate configs. Defaults to BaseConfig.
        config_data       (box.Box    ): Loaded data from config files as a 'python-box' Box. Defaults to Box().
        configs_dir       (str        ): Main configs directory to load all config files. Defaults to ConfigLoader._CONFIGS_DIR.
        extra_configs_dir (str        ): Extra configs directory to load extra config files. Defaults to None, but will use the 'PY_EXTRA_CONFIGS_DIR' environment variable if set.
        required_envs     (str        ): Required environment variables to check. Defaults to [].
        pre_load_hook     (function   ): Custom pre-load method, this method will executed before loading and validating 'config'. Defaults to ConfigLoader._PRE_LOAD_HOOK.

    Methods:
        load()                    : Load and validate every configs into 'config'.
        _load_dotenv()            : Loading environment variables from .env file, if it's exits.
        _check_required_envs()    : Check required environment variables are exist or not.
        _load_config_files()      : Load config files from 'configs_dir' into 'config_data'.
        _load_extra_config_files(): Load extra config files from 'PY_EXTRA_CONFIGS_DIR' into 'config_data'.
    """

    _ENV_FILE_PATH = os.path.join(os.getcwd(), ".env")
    _CONFIGS_DIR = os.path.join(os.getcwd(), "configs")
    _PRE_LOAD_HOOK = lambda config_data: config_data

    def __init__(
        self,
        configs_dir: str = _CONFIGS_DIR,
        config_schema: _ConfigType = BaseConfig,
        required_envs: List[str] = [],
        pre_load_hook: Callable = _PRE_LOAD_HOOK,
        env_file_path: str = _ENV_FILE_PATH,
        extra_configs_dir: Union[str, None] = None,
        auto_load: bool = False,
    ):
        """ConfigLoader constructor method.

        Args:
            configs_dir       (str,         optional): Main configs directory to load all config files. Defaults to ConfigLoader._CONFIGS_DIR.
            config_schema     (_ConfigType, optional): Main config schema class to load and validate configs. Defaults to BaseConfig.
            required_envs     (list,        optional): Required environment variables to check. Defaults to [].
            pre_load_hook     (function,    optional): Custom pre-load method, this method will executed before loading and validating 'config'. Defaults to ConfigLoader._PRE_LOAD_HOOK.
            extra_configs_dir (str,         optional): Extra configs directory to load extra config files. Defaults to None.
            auto_load         (bool,        optional): Auto load configs on init or not. Defaults to False.
        """

        self.configs_dir = configs_dir
        self.config_schema = config_schema
        self.required_envs = required_envs
        self.pre_load_hook = pre_load_hook
        self.env_file_path = env_file_path
        if extra_configs_dir:
            self.extra_configs_dir = extra_configs_dir
        self.config_data = Box()

        if auto_load:
            self.load()

    def load(self) -> Union[BaseConfig, BaseSettings, BaseModel]:
        """Load and validate every configs into 'config'.

        Returns:
            Union[BaseConfig, BaseSettings, BaseModel]: Main config object (config_schema) for project.

        Raises:
            KeyError: If a required environment variable does not exist.
            Exception: If 'pre_load_hook' or 'config_schema' failed to execute.
        """

        self._load_dotenv()
        self._check_required_envs()
        self._load_config_files()
        self._load_extra_config_files()

        try:
            self.config_data: Box = self.pre_load_hook(self.config_data)
        except Exception:
            logger.critical("Failed to execute 'pre_load_hook' method:")
            raise

        try:
            self.config: Union[
                BaseConfig, BaseSettings, BaseModel
            ] = self.config_schema(**self.config_data.to_dict())
        except Exception:
            logger.critical("Failed to init 'config_schema':")
            raise

        return self.config

    def _load_dotenv(self):
        """Loading environment variables from .env file, if it's exits."""

        if os.path.isfile(self.env_file_path):
            load_dotenv(dotenv_path=self.env_file_path, override=True, encoding="utf8")

    def _check_required_envs(self):
        """Check if required environment variables exist or not.

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

    @validate_arguments
    def _load_config_files(self, configs_dir: Union[str, None] = None):
        """Load config files from 'configs_dir' into 'config_data'.

        Args:
            configs_dir (str, optional): Main configs directory to load all config files. Defaults to ConfigLoader._CONFIGS_DIR.

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
                        self.config_data.merge_update(Box(json.load(_json_file) or {}))
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
                        self.config_data.merge_update(
                            Box(yaml.safe_load(_yaml_file) or {})
                        )
                except Exception:
                    logger.critical(
                        f"Failed to load '{_yaml_file_path}' yaml config file:"
                    )
                    raise

    def _load_extra_config_files(self):
        """Load extra config files from 'PY_EXTRA_CONFIGS_DIR' into 'config_data'.

        Raises:
            Exception: If failed to load any extra config file.
        """

        if self.extra_configs_dir is None:
            _env_extra_configs_dir = os.getenv("PY_EXTRA_CONFIGS_DIR")
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
                f"The 'config' attribute type {type(config)} is invalid, must be a <class 'BaseConfig'> or 'pydantic' <class 'BaseSettings'> or <class 'BaseModel'>."
            )

        self.__config = config

    ## config ##

    ## config_schema ##
    @property
    def config_schema(self) -> _ConfigType:
        try:
            return self.__config_schema
        except AttributeError:
            return BaseConfig

    @config_schema.setter
    def config_schema(self, config_schema: _ConfigType):
        # Check if config_schema is a class (i.e., an instance of type)
        if not isinstance(config_schema, type):
            raise TypeError("'config_schema' must be a class, not an instance.")

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
                f"The 'config_schema' attribute base class {_base_class} is invalid, must be a Type[<class 'BaseConfig'>] or 'pydantic' Type[<class 'BaseSettings'>, <class 'BaseModel'>]."
            )

        self.__config_schema = config_schema

    ## config_schema ##

    ## config_data ##
    @property
    def config_data(self) -> Union[Box, None]:
        try:
            return self.__config_data
        except AttributeError:
            return None

    @config_data.setter
    def config_data(self, config_data: Box):
        if not isinstance(config_data, Box):
            raise TypeError(
                f"The 'config_data' attribute type {type(config_data)} is invalid, must be a 'python-box' <class 'Box'>."
            )

        self.__config_data = config_data

    ## config_data ##

    ## configs_dir ##
    @property
    def configs_dir(self) -> str:
        try:
            return self.__configs_dir
        except AttributeError:
            return ConfigLoader._CONFIGS_DIR

    @configs_dir.setter
    def configs_dir(self, configs_dir: str):
        if not isinstance(configs_dir, str):
            raise TypeError(
                f"The 'configs_dir' attribute type {type(configs_dir)} is invalid, must be a <str>!"
            )

        configs_dir = configs_dir.strip()
        if configs_dir == "":
            raise ValueError("The 'configs_dir' attribute value is empty!")

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
                f"The 'extra_configs_dir' attribute type {type(extra_configs_dir)} is invalid, must be a <str>!"
            )

        extra_configs_dir = extra_configs_dir.strip()
        if extra_configs_dir == "":
            raise ValueError("The 'extra_configs_dir' attribute value is empty!")

        self.__extra_configs_dir = extra_configs_dir

    ## extra_configs_dir ##

    ## env_file_path ##
    @property
    def env_file_path(self) -> str:
        try:
            return self.__env_file_path
        except AttributeError:
            return ConfigLoader._ENV_FILE_PATH

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
            return []

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
    def pre_load_hook(self) -> Union[Callable, None]:
        try:
            return self.__pre_load
        except AttributeError:
            return ConfigLoader._PRE_LOAD_HOOK

    @pre_load_hook.setter
    def pre_load_hook(self, pre_load_hook: Callable):
        if not callable(pre_load_hook):
            raise TypeError(
                f"'pre_load_hook' argument type {type(pre_load_hook)} is invalid, should be callable <function>!"
            )

        self.__pre_load = pre_load_hook

    ## pre_load_hook ##
    ### ATTRIBUTES ###
