# -*- coding: utf-8 -*-

import os
import logging
from pathlib import Path
from typing import Callable, Tuple, Dict, Any

import pytest
import pydantic
from pydantic import Field

_has_pydantic_settings = False
if "2.0.0" <= pydantic.__version__:
    try:
        import pydantic_settings

        _has_pydantic_settings = True
    except ImportError:
        pass

try:
    from onion_config import ConfigLoader, BaseConfig, WarnEnum
except ImportError:
    from src.onion_config import ConfigLoader, BaseConfig, WarnEnum


logger = logging.getLogger(__name__)


@pytest.fixture
def config_loader() -> ConfigLoader:
    _config_loader = ConfigLoader()

    yield _config_loader

    del _config_loader


@pytest.fixture
def configs_dir(tmp_path: Path) -> Tuple[str, Dict[str, Any]]:
    _tmp_configs_dir_pl = tmp_path / "configs"
    _tmp_configs_dir_pl.mkdir()
    _tmp_json_file_pl = (_tmp_configs_dir_pl / "test.json").resolve()
    _tmp_json_file_pl.write_text(
        '{"json_test": {"str_val": "some_value", "int_val": 123} }'
    )
    _tmp_yaml_file_pl = (_tmp_configs_dir_pl / "test.yml").resolve()
    _tmp_yaml_file_pl.write_text("yaml_test: true")
    _tmp_configs_dir = str(_tmp_configs_dir_pl)
    _expected = {
        "json_test": {"str_val": "some_value", "int_val": 123},
        "yaml_test": True,
    }

    yield _tmp_configs_dir, _expected

    del (
        _tmp_configs_dir_pl,
        _tmp_json_file_pl,
        _tmp_yaml_file_pl,
        _tmp_configs_dir,
        _expected,
    )


def test_init(config_loader: ConfigLoader):
    logger.info("Testing initialization of 'ConfigLoader'...")

    assert isinstance(config_loader, ConfigLoader)
    assert isinstance(config_loader.configs_dirs, list)
    assert config_loader.configs_dirs == [ConfigLoader._CONFIGS_DIR]
    assert issubclass(config_loader.config_schema, BaseConfig)
    assert config_loader.config_schema == BaseConfig
    assert isinstance(config_loader.required_envs, list)
    assert config_loader.required_envs == []
    assert isinstance(config_loader.pre_load_hook, Callable)
    assert config_loader.pre_load_hook == ConfigLoader._PRE_LOAD_HOOK
    assert isinstance(config_loader.env_file_paths, list)
    assert config_loader.env_file_paths == [ConfigLoader._ENV_FILE_PATH]
    assert config_loader.extra_dir == None
    assert isinstance(config_loader.config_data, dict)
    assert config_loader.config_data == {}
    assert isinstance(config_loader.warn_mode, WarnEnum)
    assert config_loader.warn_mode == WarnEnum.IGNORE
    assert config_loader.config == None

    logger.info("Done: Initialization of 'ConfigLoader'.\n")


def test_load(config_loader: ConfigLoader):
    logger.info("Testing 'load' method...")

    _config: BaseConfig = config_loader.load()

    assert isinstance(_config, BaseConfig)
    assert config_loader.config == _config

    logger.info("Done: 'load' method.")


@pytest.mark.parametrize(
    "config_schema, configs_dirs, env_file_paths, required_envs, pre_load_hook, extra_dir, config_data, warn_mode, expected",
    [
        (
            BaseConfig,
            ConfigLoader._CONFIGS_DIR,
            ConfigLoader._ENV_FILE_PATH,
            [],
            lambda config_data: config_data,
            None,
            {},
            "IGNORE",
            {},
        )
    ],
)
def test_config_load(
    config_schema,
    configs_dirs,
    env_file_paths,
    required_envs,
    pre_load_hook,
    extra_dir,
    config_data,
    warn_mode,
    expected,
):
    logger.info("Testing main config cases...")

    _config = ConfigLoader(
        config_schema=config_schema,
        configs_dirs=configs_dirs,
        env_file_paths=env_file_paths,
        required_envs=required_envs,
        pre_load_hook=pre_load_hook,
        extra_dir=extra_dir,
        config_data=config_data,
        warn_mode=warn_mode,
    ).load()

    assert isinstance(_config, config_schema)
    if _has_pydantic_settings:
        assert _config.model_dump() == expected
    else:
        assert _config.dict() == expected

    logger.info("Done: Main config cases.\n")


@pytest.mark.parametrize(
    "content, expected",
    [
        ("ENV=test", "test"),
        ("DEBUG=false", "false"),
        ("TEST_ENV_VAR=123", "123"),
    ],
)
def test_load_dotenv_files(
    tmp_path: Path, config_loader: ConfigLoader, content: str, expected: str
):
    logger.info("Testing '_load_dotenv_files' method...")

    _tmp_envs_dir_pl = tmp_path / "envs"
    _tmp_envs_dir_pl.mkdir()
    _tmp_env_file_pl = (_tmp_envs_dir_pl / ".env").resolve()
    _tmp_env_file_pl.write_text(content)
    _tmp_env_path = str(_tmp_env_file_pl)

    config_loader.env_file_paths = _tmp_env_path
    config_loader._load_dotenv_files()
    _env_var = content.split("=")[0]

    assert config_loader.env_file_paths == [_tmp_env_path]
    assert os.getenv(_env_var) == expected

    logger.info("Done: '_load_dotenv_files' method.\n")


def test_check_required_envs(config_loader: ConfigLoader):
    logger.info("Testing '_check_required_envs' method...")

    os.environ["REQUIRED_ENV_VAR"] = "required_value"

    config_loader.required_envs = ["REQUIRED_ENV_VAR"]
    config_loader._check_required_envs()

    assert config_loader.required_envs == ["REQUIRED_ENV_VAR"]
    assert os.getenv("REQUIRED_ENV_VAR") == "required_value"

    with pytest.raises(KeyError):
        _none_existent_env_var = "NON_EXISTENT_ENV_VAR"
        config_loader.required_envs = [_none_existent_env_var]
        config_loader._check_required_envs()
        assert os.getenv(_none_existent_env_var) == None

    logger.info("Done: '_check_required_envs' method.\n")


def test_load_configs_dirs(
    config_loader: ConfigLoader, configs_dir: Tuple[str, Dict[str, Any]]
):
    logger.info("Testing '_load_configs_dirs' method...")

    _configs_dir, _expected = configs_dir
    config_loader.configs_dirs = [_configs_dir]
    config_loader._load_configs_dirs()

    assert isinstance(config_loader.config_data, dict)
    assert config_loader.config_data["json_test"]["str_val"] == "some_value"
    assert config_loader.config_data["json_test"]["int_val"] == 123
    assert config_loader.config_data["yaml_test"] == True
    assert config_loader.config_data == _expected

    logger.info("Done: '_load_configs_dirs' method.\n")


def test_load_extra_dir(
    tmp_path, config_loader: ConfigLoader, configs_dir: Tuple[str, Dict[str, Any]]
):
    logger.info("Testing '_load_extra_dir' method...")

    _configs_dir, _expected = configs_dir
    config_loader.configs_dirs = [_configs_dir]
    config_loader._load_configs_dirs()

    _tmp_extra_dir_pl = tmp_path / "extra_dir"
    _tmp_extra_dir_pl.mkdir()
    _tmp_yaml_file_pl = (_tmp_extra_dir_pl / "test.yaml").resolve()
    _tmp_yaml_file_pl.write_text(
        'json_test:\n  str_val: "updated_val"\n  int_val: 321\nextra_test: "extra_value"'
    )
    _tmp_extra_dir = str(_tmp_extra_dir_pl)
    _expected["json_test"]["int_val"] = 321
    _expected["json_test"]["str_val"] = "updated_val"
    _expected["extra_test"] = "extra_value"

    config_loader.extra_dir = _tmp_extra_dir
    config_loader._load_extra_dir()

    assert isinstance(config_loader.config_data, dict)
    assert config_loader.config_data["json_test"]["str_val"] == "updated_val"
    assert config_loader.config_data["json_test"]["int_val"] == 321
    assert config_loader.config_data["extra_test"] == "extra_value"
    assert config_loader.config_data == _expected

    logger.info("Done: '_load_extra_dir' method.\n")


def test_config(config_loader: ConfigLoader):
    logger.info("Testing 'config' property...")

    class _ConfigSchema(BaseConfig):
        test_var: str = Field("default_val", min_length=2, max_length=32)

    config_loader.config_schema = _ConfigSchema
    config_loader.load()

    assert isinstance(config_loader.config, _ConfigSchema)
    assert config_loader.config.test_var == "default_val"
    if _has_pydantic_settings:
        assert config_loader.config.model_dump() == {"test_var": "default_val"}
    else:
        assert config_loader.config.dict() == {"test_var": "default_val"}

    config_loader.config = _ConfigSchema(test_var="new_val")
    assert config_loader.config.test_var == "new_val"
    if _has_pydantic_settings:
        assert config_loader.config.model_dump() == {"test_var": "new_val"}
    else:
        assert config_loader.config.dict() == {"test_var": "new_val"}

    with pytest.raises(TypeError):
        config_loader.config = {"test_var": "invalid_val"}
        config_loader.config = "invalid_val"
        config_loader.config = 3.14
        config_loader.config = False
        config_loader.config = None

    logger.info("Done: 'config' property.\n")


def test_config_schema(config_loader: ConfigLoader):
    logger.info("Testing 'config_schema' property...")

    class _ConfigSchema(BaseConfig):
        pass

    config_loader.config_schema = _ConfigSchema
    assert config_loader.config_schema == _ConfigSchema

    with pytest.raises(TypeError):
        config_loader.config_schema = "invalid_val"
        config_loader.config_schema = 3.14
        config_loader.config_schema = False
        config_loader.config_schema = None

    logger.info("Done: 'config_schema' property.\n")


def test_config_data(config_loader: ConfigLoader):
    logger.info("Testing 'config_data' property...")

    _config_data = {"test_var": "test_val"}
    config_loader.config_data = _config_data

    assert isinstance(config_loader.config_data, dict)
    assert config_loader.config_data == _config_data
    assert config_loader.config_data["test_var"] == "test_val"
    assert config_loader.config_data == _config_data

    with pytest.raises(TypeError):
        config_loader.config_data = _config_data
        config_loader.config_data = "invalid_val"
        config_loader.config_data = 3.14
        config_loader.config_data = False
        config_loader.config_data = None

    logger.info("Done: 'config_data' property.\n")


def test_configs_dirs(config_loader: ConfigLoader):
    logger.info("Testing 'configs_dirs' property...")

    config_loader.configs_dirs = "/tmp/pytest/configs_dir"
    assert config_loader.configs_dirs == ["/tmp/pytest/configs_dir"]

    with pytest.raises(TypeError):
        config_loader.configs_dirs = 3.14
        config_loader.configs_dirs = False
        config_loader.configs_dirs = None

    with pytest.raises(ValueError):
        config_loader.configs_dirs = ""

    logger.info("Done: 'configs_dirs' property.\n")


def test_extra_dir(config_loader: ConfigLoader):
    logger.info("Testing 'extra_dir' property...")

    config_loader.extra_dir = "/tmp/pytest/extra_dir"
    assert config_loader.extra_dir == "/tmp/pytest/extra_dir"

    with pytest.raises(TypeError):
        config_loader.extra_dir = 3.14
        config_loader.extra_dir = False
        config_loader.extra_dir = None

    with pytest.raises(ValueError):
        config_loader.extra_dir = ""

    logger.info("Done: 'extra_dir' property.\n")


def test_env_file_paths(config_loader: ConfigLoader):
    logger.info("Testing 'env_file_paths' property...")

    config_loader.env_file_paths = "/tmp/pytest/.env"
    assert config_loader.env_file_paths == ["/tmp/pytest/.env"]

    with pytest.raises(TypeError):
        config_loader.env_file_paths = 3.14
        config_loader.env_file_paths = False
        config_loader.env_file_paths = None

    with pytest.raises(ValueError):
        config_loader.env_file_paths = ""

    logger.info("Done: 'env_file_paths' property.\n")


def test_required_envs(config_loader: ConfigLoader):
    logger.info("Testing 'required_envs' property...")

    config_loader.required_envs = ["TEST_ENV_VAR"]
    assert config_loader.required_envs == ["TEST_ENV_VAR"]

    config_loader.required_envs = []
    assert config_loader.required_envs == []

    with pytest.raises(TypeError):
        config_loader.required_envs = "invalid_val"
        config_loader.required_envs = 3.14
        config_loader.required_envs = False
        config_loader.required_envs = None

    with pytest.raises(ValueError):
        config_loader.required_envs = ["TEST_ENV_VAR", 1, None]

    logger.info("Done: 'required_envs' property.\n")


def test_pre_load_hook(config_loader: ConfigLoader):
    logger.info("Testing 'pre_load_hook' property...")

    def _pre_load_hook(config_data):
        return config_data

    config_loader.pre_load_hook = _pre_load_hook
    _config_data: dict = config_loader.pre_load_hook(config_loader.config_data)

    assert isinstance(_config_data, dict)
    assert config_loader.pre_load_hook == _pre_load_hook

    with pytest.raises(TypeError):
        config_loader.pre_load_hook = "invalid_val"
        config_loader.pre_load_hook = 3.14
        config_loader.pre_load_hook = False
        config_loader.pre_load_hook = None

    logger.info("Done: 'pre_load_hook' property.\n")
