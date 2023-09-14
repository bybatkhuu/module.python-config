# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from distutils.util import convert_path


_package_name = "onion_config"

_namespace_dict = {}
_version_path = convert_path(f"{_package_name}/__version__.py")
with open(_version_path) as _version_file:
    exec(_version_file.read(), _namespace_dict)
_package_version = _namespace_dict["__version__"]

setup(
    name=_package_name,
    packages=find_packages(),
    version=f"{_package_version}",
    license="MIT",
    description=f"'{_package_name}' is a python package that allows for easy configuration management. It allows for loading and validating configuration data from environment variables and config files in JSON and YAML formats.",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    author="Batkhuu Byambajav",
    author_email="batkhuu10@gmail.com",
    url="https://github.com/bybatkhuu/module.python-config",
    download_url=f"https://github.com/bybatkhuu/module.python-config/archive/v{_package_version}.tar.gz",
    keywords=[
        _package_name,
        "config",
        "configs",
        "dotenv",
        "python-dotenv",
        "pydantic",
        "pydantic-config",
        "pydantic-settings",
        "custom-config",
    ],
    python_requires=">=3.8",
    install_requires=[
        "python-dotenv>=1.0.0,<2.0.0",
        "PyYAML>=6.0.1,<7.0",
        "loguru>=0.7.2,<1.0.0",
        "pydantic[email]>=2.1.1,<3.0.0",
        "pydantic-settings>=2.0.3,<3.0.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
