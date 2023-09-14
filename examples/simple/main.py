#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pprint

from loguru import logger

from onion_config import ConfigLoader, BaseConfig


class ConfigSchema(BaseConfig):
    env: str = "local"


try:
    config: ConfigSchema = ConfigLoader(config_schema=ConfigSchema).load()
except Exception:
    logger.exception("Failed to load config:")
    exit(2)

if __name__ == "__main__":
    logger.info(f"App name: {config.app['name']}")
    logger.info(f"Config:\n{pprint.pformat(config.model_dump())}\n")
