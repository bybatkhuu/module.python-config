---
hide:
  - navigation
#   - toc
---

# Introduction

`onion_config` is a Python package designed for easy configuration management. It supports loading and validating configuration data from environment variables and configuration files in JSON and YAML formats. It is a `Pydantic` based custom configuration package for Python projects.

## ✨ Features

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
- Support **Pydantic-v1** and **Pydantic-v2**
