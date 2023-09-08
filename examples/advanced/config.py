# -*- coding: utf-8 -*-

from onion_config import ConfigLoader

from logger import logger
from schema import ConfigSchema


# Pre-load function to modify config data before loading and validation:
def _pre_load_hook(config_data: dict) -> dict:
    config_data["app"]["port"] = "80"
    config_data["extra_val"] = "Something extra!"
    return config_data

config = None
try:
    _config_loader = ConfigLoader(
        config_schema=ConfigSchema,
        configs_dirs=["configs", "configs_2", "/not_exists/path/configs_3"],
        env_file_paths=[".env", ".env.base", ".env.prod"],
        pre_load_hook=_pre_load_hook,
        config_data={"base": "start_value"},
        quiet=False,
    )
    # Main config object:
    config: ConfigSchema = _config_loader.load()
except Exception:
    logger.exception("Failed to load config:")
    exit(2)
