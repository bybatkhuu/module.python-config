# -*- coding: utf-8 -*-

import os
import logging

import pytest
from box import Box
from pydantic import Field

from onion_config import ConfigLoader, BaseConfig

logger = logging.getLogger(__name__)


@pytest.fixture
def config_loader():
    _config_loader = ConfigLoader()

    yield _config_loader

    del _config_loader


@pytest.fixture
def configs_dir(tmp_path):
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


def test_init(config_loader):
    logger.info("Testing initialization of 'ConfigLoader'...")

    assert isinstance(config_loader, ConfigLoader)
    assert config_loader.configs_dir == ConfigLoader._CONFIGS_DIR
    assert config_loader.config_schema == BaseConfig
    assert config_loader.required_envs == []
    assert config_loader.pre_load_hook == ConfigLoader._PRE_LOAD_HOOK
    assert config_loader.env_file_path == ConfigLoader._ENV_FILE_PATH
    assert config_loader.extra_configs_dir == None
    assert isinstance(config_loader.config_data, Box)
    assert config_loader.config == None

    logger.info("Done: initialization of 'ConfigLoader'.")


def test_load(config_loader):
    logger.info("Testing 'load' method...")

    _config: BaseConfig = config_loader.load()

    assert isinstance(_config, BaseConfig)
    assert config_loader.config == _config

    logger.info("Done: 'load' method.")


@pytest.mark.parametrize(
    "configs_dir, config_schema, required_envs, pre_load_hook, env_file_path, extra_configs_dir,  expected",
    [
        (
            ConfigLoader._CONFIGS_DIR,
            BaseConfig,
            [],
            lambda config_data: config_data,
            ConfigLoader._ENV_FILE_PATH,
            None,
            {},
        )
    ],
)
def test_config_load(
    configs_dir,
    config_schema,
    required_envs,
    pre_load_hook,
    env_file_path,
    extra_configs_dir,
    expected,
):
    logger.info("Testing main config cases...")

    _config = ConfigLoader(
        configs_dir=configs_dir,
        config_schema=config_schema,
        required_envs=required_envs,
        pre_load_hook=pre_load_hook,
        env_file_path=env_file_path,
        extra_configs_dir=extra_configs_dir,
    ).load()

    assert isinstance(_config, config_schema)
    assert _config.dict() == expected

    logger.info("Done: Main config cases.")


@pytest.mark.parametrize(
    "content, expected",
    [
        ("ENV=test", "test"),
        ("DEBUG=false", "false"),
        ("TEST_ENV_VAR=123", "123"),
    ],
)
def test_load_dotenv(tmp_path, config_loader, content, expected):
    logger.info("Testing 'load_dotenv' method...")

    _tmp_envs_dir_pl = tmp_path / "envs"
    _tmp_envs_dir_pl.mkdir()
    _tmp_env_file_pl = (_tmp_envs_dir_pl / ".env").resolve()
    _tmp_env_file_pl.write_text(content)
    _tmp_env_path = str(_tmp_env_file_pl)

    config_loader.env_file_path = _tmp_env_path
    config_loader._load_dotenv()
    _env_var = content.split("=")[0]

    assert config_loader.env_file_path == _tmp_env_path
    assert os.getenv(_env_var) == expected

    logger.info("Done: 'load_dotenv' method.")


def test_check_required_envs(config_loader):
    logger.info("Testing 'check_required_envs' method...")

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

    logger.info("Done: 'check_required_envs' method.")


def test_load_config_files(config_loader, configs_dir):
    logger.info("Testing 'load_config_files' method...")

    _configs_dir, _expected = configs_dir
    config_loader.configs_dir = _configs_dir
    config_loader._load_config_files()

    assert isinstance(config_loader.config_data, Box)
    assert config_loader.config_data.json_test.str_val == "some_value"
    assert config_loader.config_data.json_test.int_val == 123
    assert config_loader.config_data.yaml_test == True
    assert config_loader.config_data == _expected
    assert config_loader.config_data.to_dict() == _expected

    logger.info("Done: 'load_config_files' method.")


def test_load_extra_config_files(tmp_path, config_loader, configs_dir):
    logger.info("Testing 'load_extra_config_files' method...")

    _configs_dir, _expected = configs_dir
    config_loader._load_config_files(configs_dir=_configs_dir)

    _tmp_extra_configs_dir_pl = tmp_path / "extra_configs"
    _tmp_extra_configs_dir_pl.mkdir()
    _tmp_yaml_file_pl = (_tmp_extra_configs_dir_pl / "test.yaml").resolve()
    _tmp_yaml_file_pl.write_text(
        'json_test:\n  str_val: "updated_val"\n  int_val: 321\nextra_test: "extra_value"'
    )
    _tmp_extra_configs_dir = str(_tmp_extra_configs_dir_pl)
    _expected["json_test"]["int_val"] = 321
    _expected["json_test"]["str_val"] = "updated_val"
    _expected["extra_test"] = "extra_value"

    config_loader.extra_configs_dir = _tmp_extra_configs_dir
    config_loader._load_extra_config_files()

    assert isinstance(config_loader.config_data, Box)
    assert config_loader.config_data.json_test.str_val == "updated_val"
    assert config_loader.config_data.json_test.int_val == 321
    assert config_loader.config_data.extra_test == "extra_value"
    assert config_loader.config_data == _expected
    assert config_loader.config_data.to_dict() == _expected

    logger.info("Done: 'load_extra_config_files' method.")


def test_config(config_loader):
    logger.info("Testing 'config' property...")

    class _ConfigSchema(BaseConfig):
        test_var: str = Field("default_val", min_length=2, max_length=32)

    config_loader.config_schema = _ConfigSchema
    config_loader.load()

    assert isinstance(config_loader.config, _ConfigSchema)
    assert config_loader.config.test_var == "default_val"
    assert config_loader.config.dict() == {"test_var": "default_val"}

    config_loader.config = _ConfigSchema(test_var="new_val")
    assert config_loader.config.test_var == "new_val"
    assert config_loader.config.dict() == {"test_var": "new_val"}

    with pytest.raises(TypeError):
        config_loader.config = {"test_var": "invalid_val"}
        config_loader.config = "invalid_val"
        config_loader.config = 3.14
        config_loader.config = False
        config_loader.config = None

    logger.info("Done: 'config' property.")


def test_config_schema(config_loader):
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

    logger.info("Done: 'config_schema' property.")


def test_config_data(config_loader):
    logger.info("Testing 'config_data' property...")

    _config_data_dict = {"test_var": "test_val"}
    _config_data = Box(_config_data_dict)
    config_loader.config_data = _config_data

    assert isinstance(config_loader.config_data, Box)
    assert config_loader.config_data == _config_data
    assert config_loader.config_data.test_var == "test_val"
    assert config_loader.config_data.to_dict() == _config_data_dict

    with pytest.raises(TypeError):
        config_loader.config_data = _config_data_dict
        config_loader.config_data = "invalid_val"
        config_loader.config_data = 3.14
        config_loader.config_data = False
        config_loader.config_data = None

    logger.info("Done: 'config_data' property.")


def test_configs_dir(config_loader):
    logger.info("Testing 'configs_dir' property...")

    config_loader.configs_dir = "/tmp/pytest/configs_dir"
    assert config_loader.configs_dir == "/tmp/pytest/configs_dir"

    with pytest.raises(TypeError):
        config_loader.configs_dir = 3.14
        config_loader.configs_dir = False
        config_loader.configs_dir = None

    with pytest.raises(ValueError):
        config_loader.configs_dir = ""

    logger.info("Done: 'configs_dir' property.")


def test_extra_configs_dir(config_loader):
    logger.info("Testing 'extra_configs_dir' property...")

    config_loader.extra_configs_dir = "/tmp/pytest/extra_configs_dir"
    assert config_loader.extra_configs_dir == "/tmp/pytest/extra_configs_dir"

    with pytest.raises(TypeError):
        config_loader.extra_configs_dir = 3.14
        config_loader.extra_configs_dir = False
        config_loader.extra_configs_dir = None

    with pytest.raises(ValueError):
        config_loader.extra_configs_dir = ""

    logger.info("Done: 'extra_configs_dir' property.")


def test_env_file_path(config_loader):
    logger.info("Testing 'env_file_path' property...")

    config_loader.env_file_path = "/tmp/pytest/.env"
    assert config_loader.env_file_path == "/tmp/pytest/.env"

    with pytest.raises(TypeError):
        config_loader.env_file_path = 3.14
        config_loader.env_file_path = False
        config_loader.env_file_path = None

    with pytest.raises(ValueError):
        config_loader.env_file_path = ""

    logger.info("Done: 'env_file_path' property.")


def test_required_envs(config_loader):
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

    logger.info("Done: 'required_envs' property.")


def test_pre_load_hook(config_loader):
    logger.info("Testing 'pre_load_hook' property...")

    def _pre_load_hook(config_data):
        return config_data

    config_loader.pre_load_hook = _pre_load_hook
    _config_data: Box = config_loader.pre_load_hook(config_loader.config_data)

    assert isinstance(_config_data, Box)
    assert config_loader.pre_load_hook == _pre_load_hook

    with pytest.raises(TypeError):
        config_loader.pre_load_hook = "invalid_val"
        config_loader.pre_load_hook = 3.14
        config_loader.pre_load_hook = False
        config_loader.pre_load_hook = None

    logger.info("Done: 'pre_load_hook' property.")
