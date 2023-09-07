#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pprint
import logging
from enum import Enum
from typing import Union

from pydantic import Field, SecretStr
from pydantic_settings import SettingsConfigDict

from onion_config import ConfigLoader, BaseConfig


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


# Pre-load function to modify config data before loading and validation:
def _pre_load_hook(config_data: dict) -> dict:
    config_data["app"]["port"] = "80"
    config_data["extra_val"] = "Something extra!"

    return config_data


# Environments as Enum:
class EnvEnum(str, Enum):
    LOCAL = "local"
    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


# App config schema:
class AppConfig(BaseConfig):
    name: str = Field("App", min_length=2, max_length=32)
    bind_host: str = Field("localhost", min_length=2, max_length=128)
    port: int = Field(8000, ge=80, lt=65536)
    secret: SecretStr = Field(..., min_length=8, max_length=64)
    version: str = Field(..., min_length=5, max_length=16)
    description: Union[str, None] = Field(None, min_length=4, max_length=64)

    model_config = SettingsConfigDict(extra="ignore", env_prefix="APP_")


# Main config schema:
class ConfigSchema(BaseConfig):
    env: EnvEnum = Field(EnvEnum.LOCAL)
    debug: bool = Field(False)
    app: AppConfig = Field(...)


if __name__ == "__main__":
    try:
        # Main 'config' object for usage:
        config: ConfigSchema = ConfigLoader(
            config_schema=ConfigSchema, pre_load_hook=_pre_load_hook
        ).load()
    except Exception:
        logger.exception("Failed to load config:")
        exit(2)

    logger.info(f" ENV: {config.env}")
    logger.info(f" DEBUG: {config.debug}")
    logger.info(f" Extra: {config.extra_val}")
    logger.info(f" Logger: {config.logger}")
    logger.info(f" App: {config.app}")
    logger.info(f" Secret: '{config.app.secret.get_secret_value()}'\n")
    logger.info(f" Config:\n{pprint.pformat(config.model_dump())}\n")

    try:
        # This will raise ValidationError
        config.app.port = 8443
    except Exception as e:
        logger.error(f" {e}\n")
