# -*- coding: utf-8 -*-

from enum import Enum
from typing import Union

import pydantic
from pydantic import Field, SecretStr

_has_pydantic_settings = False
if "2.0.0" <= pydantic.__version__:
    try:
        from pydantic_settings import SettingsConfigDict

        _has_pydantic_settings = True
    except ImportError:
        pass

from onion_config import BaseConfig


# Environments as Enum:
class EnvEnum(str, Enum):
    LOCAL = "local"
    DEVELOPMENT = "development"
    TEST = "test"
    DEMO = "demo"
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

    if _has_pydantic_settings:
        model_config = SettingsConfigDict(extra="ignore", env_prefix="APP_")
    else:

        class Config:
            extra = "ignore"
            env_prefix = "APP_"


# Main config schema:
class ConfigSchema(BaseConfig):
    env: EnvEnum = Field(EnvEnum.LOCAL)
    debug: bool = Field(False)
    app: AppConfig = Field(...)
