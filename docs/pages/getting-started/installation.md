# 🛠 Installation

## 1. 📥 Download or clone the repository

> [!TIP]
> Skip this step, if you're going to install the package directly from **PyPi** or **GitHub** repository.

**1.1.** Prepare projects directory (if not exists):

```sh
# Create projects directory:
mkdir -pv ~/workspaces/projects

# Enter into projects directory:
cd ~/workspaces/projects
```

**1.2.** Follow one of the below options **[A]**, **[B]** or **[C]**:

**OPTION A.** Clone the repository:

```sh
git clone https://github.com/bybatkhuu/module.python-config.git && \
    cd module.python-config
```

**OPTION B.** Clone the repository (for **DEVELOPMENT**: git + ssh key):

```sh
git clone git@github.com:bybatkhuu/module.python-config.git && \
    cd module.python-config
```

**OPTION C.** Download source code:

1. Download archived **zip** file from [**releases**](https://github.com/bybatkhuu/module.python-config/releases).
2. Extract it into the projects directory.

## 2. 📦 Install the package

> [!NOTE]
> Choose one of the following methods to install the package **[A ~ E]**:

**OPTION A.** [**RECOMMENDED**] Install from **PyPi**:

> [!WARNING]
> If you wanted to use **Pydantic-v1**, but if you already installed `pydantic-settings` and `pydantic-core`, remove it before installing **Pydantic-v1**:

```sh
pip uninstall -y pydantic-settings
pip uninstall -y pydantic-core

# Then install with Pydantic-v1:
pip install -U onion-config[pydantic-v1]
```

> [!WARNING]
> If you wanted to use **Pydantic-v2**, but if you already installed `onion-config` package just by \
> *`pip install -U onion-config`* command, and this will not install `pydantic-settings`. \
> For this case, '**`env_prefix`**' **WILL NOT WORK** for `BaseConfig` or `BaseSettings` without `pydantic-settings`! This is Pydantic-v2's problem, and there could be some other problems. \
> So fix these issues re-install `onion-config` with `pydantic-settings`:

```sh
# Install with pydantic-settings for Pydantic-v2:
pip install -U onion-config[pydantic-settings]
```

**OPTION B.** Install latest version directly from **GitHub** repository:

```sh
# Pydantic-v1:
pip install git+https://github.com/bybatkhuu/module.python-config.git[pydantic-v1]

# Pydantic-v2:
pip install git+https://github.com/bybatkhuu/module.python-config.git[pydantic-settings]
```

**OPTION C.** Install from the downloaded **source code**:

```sh
# Install directly from the source code:
# Pydantic-v1:
pip install .[pydantic-v1]
# Pydantic-v2:
pip install .[pydantic-settings]

# Or install with editable mode (for DEVELOPMENT):
# Pydantic-v1:
pip install -e .[pydantic-v1]
# Pydantic-v2:
pip install -e .[pydantic-settings]
```

**OPTION D.** Install from **pre-built release** files:

1. Download **`.whl`** or **`.tar.gz`** file from [**releases**](https://github.com/bybatkhuu/module.python-config/releases)
2. Install with pip:

```sh
# Pydantic-v1:
# Install from .whl file:
pip install ./onion_config-[VERSION]-py3-none-any.whl[pydantic-v1]
# Or install from .tar.gz file:
pip install ./onion_config-[VERSION].tar.gz[pydantic-v1]

# Pydantic-v2:
# Install from .whl file:
pip install ./onion_config-[VERSION]-py3-none-any.whl[pydantic-settings]
# Or install from .tar.gz file:
pip install ./onion_config-[VERSION].tar.gz[pydantic-settings]
```

**OPTION E.** Copy the **module** into the project directory (for **testing**):

```sh
# Install python dependencies:
pip install -r ./requirements/requirements.core.txt

# Pydantic-v1:
pip install -r ./requirements/requirements.pydantic-v1.txt
# Pydantic-v2:
pip install -r ./requirements/requirements.pydantic-settings.txt

# Copy the module source code into the project:
cp -r ./src/onion_config [PROJECT_DIR]
# For example:
cp -r ./src/onion_config /some/path/project/
```
