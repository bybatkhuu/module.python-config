# onion_config

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/bybatkhuu/mod.python-config/2.build-publish.yml)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/onion-config)](https://pypi.org/project/onion-config)
[![PyPI](https://img.shields.io/pypi/v/onion-config)](https://pypi.org/project/onion-config)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/bybatkhuu/mod.python-config)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/onion-config)](https://pypi.org/project/onion-config)

`onion_config` is a Python package that allows for easy configuration management. It allows for loading and validating configuration data from environment variables and config files in JSON and YAML formats.

`Pydantic` based custom config package for python projects.

## Features

- **Main config** based on **Pydantic schema** - <https://pypi.org/project/pydantic>
- Load **environment variables** - <https://pypi.org/project/python-dotenv>
- Config data based on **Python-box** - <https://pypi.org/project/python-box>
- Load configs from **YAML** and **JSON** files
- Update the default config with additional configurations (**`extra_configs`** directory)
- **Pre-load hook** function to modify config data before loading and validation
- **Validate config** values with **Pydantic validators**
- Config as **dictionary** or **Pydantic model** (with type hints)
- **Pre-defined** base config schema for common config (**`BaseConfig`**)
- **Base** for custom config loader (**`ConfigLoader`**)

---

## Installation

### 1. Prerequisites

- **Python (>= v3.7)**
- **PyPi (>= v21)**

### 2. Install onion-config package

Choose one of the following methods to install the package **[A ~ F]**:

**A.** [**RECOMMENDED**] Install from **PyPi**

```sh
# Install or upgrade package:
pip install -U onion-config
```

**B.** Install latest version from **GitHub**

```sh
# Install package by git:
pip install git+https://github.com/bybatkhuu/mod.python-config.git
```

**C.** Install from **pre-built release** files

1. Download **`.whl`** or **`.tar.gz`** file from **releases** - <https://github.com/bybatkhuu/mod.python-config/releases>
2. Install with pip:

```sh
# Install from .whl file:
pip install ./onion_config-[VERSION]-py3-none-any.whl
# Or install from .tar.gz file:
pip install ./onion_config-[VERSION].tar.gz
```

**D.** Install from **source code** by building package

```sh
# Clone repository by git:
git clone https://github.com/bybatkhuu/mod.python-config.git onion_config
cd ./onion_config

# Install python build tool:
pip install -U pip build

# Build python package:
python -m build

_VERSION=$(./scripts/get-version.sh)

# Install from .whl file:
pip install ./dist/onion_config-${_VERSION}-py3-none-any.whl
# Or install from .tar.gz file:
pip install ./dist/onion_config-${_VERSION}.tar.gz
```

**E.** Install with pip editable **development mode** (from source code)

```sh
# Clone repository by git:
git clone https://github.com/bybatkhuu/mod.python-config.git onion_config
cd ./onion_config

# Install with editable development mode:
pip install -e .
```

**F.** Manually add to **PYTHONPATH** (not recommended)

```sh
# Clone repository by git:
git clone https://github.com/bybatkhuu/mod.python-config.git onion_config
cd ./onion_config

# Install python dependencies:
< ./requirements.txt grep -v '^#' | xargs -t -L 1 pip install

# Add current path to PYTHONPATH:
export PYTHONPATH="${PWD}:${PYTHONPATH}"
```

## Usage/Examples

### **Simple**

To use `onion_config`, import the `ConfigLoader` class from the package:

```python
from onion_config import ConfigLoader
```

You can then create an instance of `ConfigLoader`:

```python
config_loader = ConfigLoader(auto_load=True)
```

This will automatically load configuration data from environment variables and config files located in the default directory (`'./configs'`). The configuration data can then be accessed via the `config` property of the `ConfigLoader` instance:

```python
config = config_loader.config
```

### **Advanced**

[**`configs/config.yml`**](https://github.com/bybatkhuu/mod.python-config/blob/main/examples/configs/config.yml):

```yaml
env: production

app:
  bind_host: "0.0.0.0"
  version: "0.0.1"
  ignore_val: "Ignore me"

logger:
  output: "stdout"
```

[**`configs/logger.json`**](https://github.com/bybatkhuu/mod.python-config/blob/main/examples/configs/logger.json):

```json
{
    "logger":
    {
        "level": "info",
        "output": "file"
    }
}
```

[**`.env`**](https://github.com/bybatkhuu/mod.python-config/blob/main/examples/.env):

```sh
ENVIRONMENT=development

DEBUG=true

APP_NAME="New App"
APP_SECRET="my_secret"
```

[**`main.py`**](https://github.com/bybatkhuu/mod.python-config/blob/main/examples/main.py):

```python
import sys
import pprint
import logging
from enum import Enum
from typing import Union

from box import Box
from pydantic import Field, SecretStr

from onion_config import ConfigLoader, BaseConfig


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


# Pre-load function to modify config data before loading and validation:
def _pre_load_hook(config_data: Box) -> Box:
    config_data.app.port = "80"
    config_data.extra_val = "Something extra!"

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
    secret: str = Field(..., min_length=8, max_length=64)
    version: SecretStr = Field(..., min_length=5, max_length=16)
    description: Union[str, None] = Field(None, min_length=4, max_length=64)

    class Config:
        extra = "ignore"
        env_prefix = "APP_"


# Main config schema:
class ConfigSchema(BaseConfig):
    env: EnvEnum = Field(EnvEnum.LOCAL, env="ENVIRONMENT")
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
    logger.info(f" App: {config.app}\n")
    logger.info(f" Config:\n{pprint.pformat(config.dict())}\n")

    try:
        # This will raise ValidationError
        config.app.port = 8443
    except Exception as e:
        logger.error(f" {e}\n")
```

Run the [`example`](https://github.com/bybatkhuu/mod.python-config/tree/main/examples):

```sh
cd ./examples
python ./main.py
```

Output:

```txt
INFO:__main__: ENV: development
INFO:__main__: DEBUG: True
INFO:__main__: Extra: Something extra!
INFO:__main__: Logger: {'level': 'info', 'output': 'stdout'}
INFO:__main__: App: name='New App' bind_host='0.0.0.0' port=80 secret='my_secret' version=SecretStr('**********') description=None

INFO:__main__: Config:
{'app': {'bind_host': '0.0.0.0',
         'description': None,
         'name': 'New App',
         'port': 80,
         'secret': 'my_secret',
         'version': SecretStr('**********')},
 'debug': True,
 'env': <EnvEnum.DEVELOPMENT: 'development'>,
 'extra_val': 'Something extra!',
 'logger': {'level': 'info', 'output': 'stdout'}}

ERROR:__main__: "AppConfig" is immutable and does not support item assignment
```

---

## Running Tests

To run tests, run the following command:

```sh
python -m pytest -sv
```

These tests are designed to validate the functionality and reliability of the onion-config package.

## Environment Variables

You can use the following environment variables inside [**`.env.example`**](https://github.com/bybatkhuu/mod.python-config/blob/main/.env.example) file:

```sh
PY_EXTRA_CONFIGS_DIR="./extra_configs"
```

## Documentation

- [onion_config](https://github.com/bybatkhuu/mod.python-config/blob/main/docs/README.md)
- [scripts](https://github.com/bybatkhuu/mod.python-config/blob/main/docs/scripts/README.md)

---

## References

- <https://docs.pydantic.dev>
- <https://github.com/pydantic/pydantic>
- <https://saurabh-kumar.com/python-dotenv>
- <https://github.com/theskumar/python-dotenv>
- <https://github.com/cdgriffith/Box/wiki>
- <https://github.com/cdgriffith/Box>
- <https://packaging.python.org/tutorials/packaging-projects>
