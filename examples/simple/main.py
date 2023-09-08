#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pprint
import logging

from onion_config import ConfigLoader, BaseConfig


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigSchema(BaseConfig):
    env: str = "local"


try:
    config: ConfigSchema = ConfigLoader(config_schema=ConfigSchema).load()
except Exception:
    logger.exception("Failed to load config:")
    exit(2)

if __name__ == "__main__":
    logger.info(f" App name: {config.app['name']}")
    logger.info(f" Config:\n{pprint.pformat(config.model_dump())}\n")
