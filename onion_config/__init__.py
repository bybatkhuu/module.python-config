# -*- coding: utf-8 -*-

import warnings

import pydantic

from ._base import ConfigLoader, BaseConfig, WarnEnum, __version__


if "2.0.0" <= pydantic.__version__:
    try:
        import pydantic_settings
    except ImportError:
        with warnings.catch_warnings():
            # warnings.simplefilter("default", RuntimeWarning)
            warnings.warn(
                "`[33mpydantic-settings[0m` is not installed for [33mPydantic-v2[0m.\n"
                "[33mBEWARE[0m: If you didn't install `[33mpydantic-settings[0m`, `[31menv_prefix[0m` for `BaseConfig` or `BaseSettings` [31mWILL NOT WORK! This is Pydantic-v2's problem.[0m\n"
                "If you want to use [33mPydantic-v1[0m (recommended), use `[32mpip install onion-config[pydantic-v1][0m` to install it. But if you already installed `[33mpydantic-settings[0m`, remove it before installing [33mPydantic-v1[0m: `[32mpip uninstall -y pydantic-settings[0m`.\n"
                "If you want to use [33mPydantic-v2[0m, use `[32mpip install onion-config[pydantic-settings][0m` to install it.\n",
                RuntimeWarning,
            )

__all__ = ["ConfigLoader", "BaseConfig", "WarnEnum", "__version__"]
