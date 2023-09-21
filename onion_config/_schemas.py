# -*- coding: utf-8 -*-

from typing import Tuple, Type

import pydantic

_has_pydantic_settings = False
if "2.0.0" <= pydantic.__version__:
    try:
        from pydantic_settings import (
            BaseSettings,
            SettingsConfigDict,
            PydanticBaseSettingsSource,
        )

        _has_pydantic_settings = True
    except ImportError:
        from pydantic.v1 import BaseSettings
        from pydantic.v1.env_settings import SettingsSourceCallable
else:
    from pydantic import BaseSettings
    from pydantic.env_settings import SettingsSourceCallable


class BaseConfig(BaseSettings):
    if _has_pydantic_settings:
        model_config = SettingsConfigDict(
            extra="allow", frozen=True, arbitrary_types_allowed=True
        )

        @classmethod
        def settings_customise_sources(
            cls,
            settings_cls: Type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
        ) -> Tuple[PydanticBaseSettingsSource, ...]:
            return dotenv_settings, env_settings, init_settings, file_secret_settings

    else:

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
