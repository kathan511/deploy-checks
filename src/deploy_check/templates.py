"""File templates for creating missing files."""

FILE_TEMPLATES = {
    "VERSION": """0.1.0
""",
    "bumpversion_cfg": """[bumpversion]
current_version = 0.1.0
commit = True
tag = True
tag_name = v{new_version}

[bumpversion:file:./VERSION]

[bumpversion:file:./README.md]

[bumpversion:file:./_setup.py]

[bumpversion:file:./pyproject.toml]

[bumpversion:file:./uv.lock]
""",
    "setup_py": '''"""Setup script for the project."""

__version__ = "0.1.0"

# Add your setup configuration here
''',
    "entrypoint_sh": """#!/usr/bin/env bash
set -euo pipefail

# Load environment variables
source env.sh

# Main entrypoint logic
echo "Starting application..."

# Add your entrypoint commands here
python main.py "$@"
""",
    "env_sh": """#!/usr/bin/env bash
# Environment configuration

export MODE="development"
export CONFIG="config/app.config"

# Add additional environment variables below
""",
    "readme_md": """# Project Name

Version: 0.1.0

## Description

Add your project description here.

## Installation

```bash
# Installation instructions
```

## Usage

```bash
# Usage examples
```

## Development

```bash
# Development setup
```

## License

MIT
""",
    "app_config": """# Application Configuration
# =========================

[app]
name = myapp
debug = false

[database]
host = localhost
port = 5432

[logging]
level = INFO
format = %(asctime)s - %(name)s - %(levelname)s - %(message)s
""",
    "environment_yml": """name: myproject
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - pip
  - pip:
    - ruff
""",
    "pyproject_toml": """[project]
name = "myproject"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.11"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]
ignore = []
""",
    "python_version": """3.11
""",
}
