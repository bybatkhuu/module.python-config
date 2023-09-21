#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pprint

from loguru import logger

try:
    import pydantic_settings

    _has_pydantic_settings = True
except ImportError:
    _has_pydantic_settings = False

from config import config


if __name__ == "__main__":
    logger.info(f"All: {config}")
    logger.info(f"ENV: {config.env}")
    logger.info(f"DEBUG: {config.debug}")
    logger.info(f"Extra: {config.extra_val}")
    logger.info(f"Logger: {config.logger}")
    logger.info(f"App: {config.app}")
    logger.info(f"Secret: '{config.app.secret.get_secret_value()}'\n")

    if _has_pydantic_settings:
        logger.info(f"Config:\n{pprint.pformat(config.model_dump())}\n")
    else:
        logger.info(f"Config:\n{pprint.pformat(config.dict())}\n")

    try:
        # This will raise ValidationError
        config.app.port = 8443
    except Exception as e:
        logger.error(f"{e}\n")
