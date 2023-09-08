# onion_config

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/bybatkhuu/mod.python-config/2.build-publish.yml?logo=GitHub)](https://github.com/bybatkhuu/mod.python-config/actions/workflows/2.build-publish.yml)
[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/bybatkhuu/mod.python-config?logo=GitHub)](https://github.com/bybatkhuu/mod.python-config/releases)
[![PyPI](https://img.shields.io/pypi/v/onion-config?logo=PyPi)](https://pypi.org/project/onion-config)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/onion-config?logo=Python)](https://docs.conda.io/en/latest/miniconda.html)

`onion_config` is a python package that allows for easy configuration management. It allows for loading and validating configuration data from environment variables and config files in JSON and YAML formats.

`Pydantic` based custom config package for python projects.

## Features

- **Main config** based on **Pydantic schema** - <https://pypi.org/project/pydantic>
- Load **environment variables** - <https://pypi.org/project/python-dotenv>
- Load from **multiple** configs directories
- Load configs from **YAML** and **JSON** files
- Update the default config with additional configurations (**`extra_dir`** directory)
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
pip install -r ./requirements.txt

# Add current path to PYTHONPATH:
export PYTHONPATH="${PWD}:${PYTHONPATH}"
```

## Usage/Examples

To use `onion_config`, import the `ConfigLoader` class from the package:

```python
from onion_config import ConfigLoader, BaseConfig
```

You can create an instance of `ConfigLoader` with `auto_load` flag. This will automatically load configuration data from environment variables and config files located in the default directory (`'./configs'`). The configuration data can then be accessed via the `config` property of the `ConfigLoader` instance:

```python
config: BaseConfig = ConfigLoader(auto_load=True).config
```

### **Simple**

[**`.env`**](https://github.com/bybatkhuu/mod.python-config/blob/main/examples/simple/.env)

```sh
ENV=production
```

[**`configs/1.base.yml`**](https://github.com/bybatkhuu/mod.python-config/blob/main/examples/simple/configs/1.base.yml):

```yaml
env: test

app:
  name: "My App"
  version: "0.0.1"
  nested:
    key: "value"
```

[**`configs/2.extra.yml`**](https://github.com/bybatkhuu/mod.python-config/blob/main/examples/simple/configs/2.extra.yml):

```yaml
app:
  name: "New App"
  nested:
    some: "value"
  description: "Description of my app."

another_val:
  extra: 1
```

[**`main.py`**](https://github.com/bybatkhuu/mod.python-config/blob/main/examples/simple/main.py)

```python
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
```

Run the [**`examples/simple`**](https://github.com/bybatkhuu/mod.python-config/tree/main/examples/simple):

```sh
cd ./examples/simple

python ./main.py
```

Output:

```txt
INFO:__main__: App name: New App
INFO:__main__: Config:
{'another_val': {'extra': 1},
 'app': {'description': 'Description of my app.',
         'name': 'New App',
         'nested': {'key': 'value', 'some': 'value'},
         'version': '0.0.1'},
 'env': 'production'}
```

### **Advanced**

[**`.env.base`**](https://github.com/bybatkhuu/mod.python-config/blob/main/examples/advanced/.env.base):

```sh
ENV=development
DEBUG=true
APP_NAME="Old App"
ONION_CONFIG_EXTRA_DIR="extra_configs"
```

[**`.env.prod`**](https://github.com/bybatkhuu/mod.python-config/blob/main/examples/advanced/.env.prod):

```sh
ENV=production
APP_NAME="New App"
APP_SECRET="my_secret"
```

[**`configs/config.yml`**](https://github.com/bybatkhuu/mod.python-config/blob/main/examples/advanced/configs/config.yml):

```yaml
env: local

app:
  name: "My App"
  port: 9000
  bind_host: "0.0.0.0"
  version: "0.0.1"
  ignore_val: "Ignore me"

logger:
  output: "file"
```

[**`configs/logger.json`**](https://github.com/bybatkhuu/mod.python-config/blob/main/examples/advanced/configs/logger.json):

```json
{
    "logger": {
        "level": "info",
        "output": "stdout"
    }
}
```

[**`configs_2/config.yml`**](https://github.com/bybatkhuu/mod.python-config/blob/main/examples/advanced/configs_2/config.yml):

```yaml
extra:
  config:
    key1: 1
```

[**`configs_2/config_2.yml`**](https://github.com/bybatkhuu/mod.python-config/blob/main/examples/advanced/configs_2/config_2.yml):

```yaml
extra:
  config:
    key2: 2
```

[**`extra_configs/extra.json`**](https://github.com/bybatkhuu/mod.python-config/blob/main/examples/advanced/extra_configs/extra.json):

```json
{
    "extra": {
        "type": "json"
    }
}
```

[**`logger.py`**](https://github.com/bybatkhuu/mod.python-config/blob/main/examples/advanced/logger.py):

```python
import sys
import logging

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)
```

[**`schema.py`**](https://github.com/bybatkhuu/mod.python-config/blob/main/examples/advanced/schema.py):

```python
from enum import Enum
from typing import Union

from pydantic import Field, SecretStr
from pydantic_settings import SettingsConfigDict

from onion_config import BaseConfig


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
```

[**`config.py`**](https://github.com/bybatkhuu/mod.python-config/blob/main/examples/advanced/config.py):

```python
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
        configs_dirs=["configs", "configs_2", "/not_exixts/path/configs_3"],
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
```

[**`app.py`**](https://github.com/bybatkhuu/mod.python-config/blob/main/examples/advanced/app.py):

```python
import pprint

from config import config
from logger import logger


if __name__ == "__main__":
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
```

Run the [**`examples/advanced`**](https://github.com/bybatkhuu/mod.python-config/tree/main/examples/advanced):

```sh
cd ./examples/advanced

python ./app.py
```

Output:

```txt
WARNING:onion_config._base:'/home/user/workspaces/projects/onion_config/examples/advanced/.env' file is not exist!
WARNING:onion_config._base:'/not_exixts/path/configs_3' directory is not exist!
INFO:logger: ENV: production
INFO:logger: DEBUG: True
INFO:logger: Extra: Something extra!
INFO:logger: Logger: {'output': 'stdout', 'level': 'info'}
INFO:logger: App: name='New App' bind_host='0.0.0.0' port=80 secret=SecretStr('**********') version='0.0.1' description=None
INFO:logger: Secret: 'my_secret'

INFO:logger: Config:
{'app': {'bind_host': '0.0.0.0',
         'description': None,
         'name': 'New App',
         'port': 80,
         'secret': SecretStr('**********'),
         'version': '0.0.1'},
 'base': 'start_value',
 'debug': True,
 'env': <EnvEnum.PRODUCTION: 'production'>,
 'extra': {'config': {'key1': 1, 'key2': 2}, 'type': 'json'},
 'extra_val': 'Something extra!',
 'logger': {'level': 'info', 'output': 'stdout'}}

ERROR:logger: 1 validation error for AppConfig
port
  Instance is frozen [type=frozen_instance, input_value=8443, input_type=int]
```

---

## Running Tests

To run tests, run the following command:

```sh
# Install python test dependencies:
pip install -r ./requirements.test.txt

# Run tests:
python -m pytest -sv
```

## FAQ

### What is the order of loading config?

Load order:

1. Load all dotenv files from `env_file_paths` into environment variables.
2. Check if required environment variables exist or not.
3. Load all config files from `configs_dirs` into `config_data`.
4. Load extra config files from `extra_dir` into `config_data`.
5. Execute `pre_load_hook` method to modify `config_data`.
6. Init `config_schema` with `config_data` into final `config`.

## Environment Variables

You can use the following environment variables inside [**`.env.example`**](https://github.com/bybatkhuu/mod.python-config/blob/main/.env.example) file:

```sh
ONION_CONFIG_EXTRA_DIR="./extra_dir"
```

## Documentation

- [docs](https://github.com/bybatkhuu/mod.python-config/blob/main/docs/README.md)
- [scripts](https://github.com/bybatkhuu/mod.python-config/blob/main/docs/scripts/README.md)

---

## References

- <https://docs.pydantic.dev>
- <https://github.com/pydantic/pydantic>
- <https://docs.pydantic.dev/latest/usage/pydantic_settings>
- <https://github.com/pydantic/pydantic-settings>
- <https://saurabh-kumar.com/python-dotenv>
- <https://github.com/theskumar/python-dotenv>
- <https://packaging.python.org/tutorials/packaging-projects>
