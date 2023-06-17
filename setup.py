# -*- coding: utf-8 -*-

from setuptools import setup
from distutils.util import convert_path


_package_name = "onion_config"

_namespace_dict = {}
_version_path = convert_path(f"{_package_name}/__version__.py")
with open(_version_path) as _version_file:
    exec(_version_file.read(), _namespace_dict)
_package_version = _namespace_dict["__version__"]

setup(
    name=_package_name,
    packages=[_package_name],
    version=f"{_package_version}",
    license="MIT",
    description="Pydantic based custom config package (onion_config) for python projects.",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    author="Batkhuu Byambajav",
    author_email="batkhuu10@gmail.com",
    url="https://github.com/bybatkhuu/mod.python-config",
    download_url=f"https://github.com/bybatkhuu/mod.python-config/archive/v{_package_version}.tar.gz",
    keywords=[
        _package_name,
        "config",
        "configs",
        "python-dotenv",
        "python-box",
        "pydantic",
        "pydantic-config",
        "custom-config",
    ],
    python_requires=">=3.7",
    install_requires=[
        "python-dotenv>=1.0.0",
        "PyYAML>=6.0",
        "email-validator==1.3.1",
        "python-box>=7.0.1",
        "pydantic==1.10.9",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
