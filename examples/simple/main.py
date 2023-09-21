#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pprint

from loguru import logger

try:
    import pydantic_settings

    _has_pydantic_settings = True
except ImportError:
    _has_pydantic_settings = False

from onion_config import ConfigLoader, BaseConfig


class ConfigSchema(BaseConfig):
    env: str = "local"


try:
    config: ConfigSchema = ConfigLoader(config_schema=ConfigSchema).load()
except Exception:
    logger.exception("Failed to load config:")
    exit(2)

if __name__ == "__main__":
    logger.info(f"All: {config}")
    logger.info(f"App name: {config.app['name']}")

    if _has_pydantic_settings:
        logger.info(f"Config:\n{pprint.pformat(config.model_dump())}\n")
    else:
        logger.info(f"Config:\n{pprint.pformat(config.dict())}\n")
