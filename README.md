# deploy-check 🔍

A Terminal UI tool for pre-deployment validation. Checks your project for required files, configuration, and standards compliance before deploying.

![Screenshot](screenshot.png)

## Features

- ✅ **Visual Checklist** - See all requirements at a glance
- 🔧 **One-Click Fix** - Create missing files from templates
- 🐍 **Venv Support** - Checks for conda, uv, or other environments
- 🧹 **Lint Integration** - Run ruff linter from the UI
- 🎨 **Beautiful TUI** - Modern terminal interface with keyboard shortcuts

## Installation

### Quick Install (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/yourorg/deploy-checks/main/install.sh | bash
```

### Via pip/pipx

```bash
# Using pipx (recommended for CLI tools)
pipx install git+https://github.com/yourorg/deploy-checks.git

# Using pip
pip install git+https://github.com/yourorg/deploy-checks.git

# Using uv
uv tool install git+https://github.com/yourorg/deploy-checks.git
```

### Via Homebrew

```bash
brew tap yourorg/tools
brew install deploy-check
```

### From Source

```bash
git clone https://github.com/yourorg/deploy-checks.git
cd deploy-checks
pip install -e .
```

## Usage

### Run the TUI

```bash
# Check current directory
deploy-check

# Check a specific directory
deploy-check /path/to/your/project
```

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `a` | Create all missing files |
| `l` | Run linter |
| `r` | Refresh checks |
| `q` | Quit |

### Setup as Git Hook

Run deploy-check automatically before every `git push`:

```bash
# In your project repository
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
deploy-check
exit $?
EOF
chmod +x .git/hooks/pre-push
```

For team-wide hooks, add to a tracked directory:

```bash
mkdir -p .githooks
cat > .githooks/pre-push << 'EOF'
#!/bin/bash
deploy-check
exit $?
EOF
chmod +x .githooks/pre-push
git config core.hooksPath .githooks
```

## What It Checks

### Required Files
- `VERSION` - Version number file
- `.bumpversion.cfg` - Version bump configuration
- `_setup.py` - Setup script
- `bin/entrypoint.sh` - Application entrypoint
- `env.sh` - Environment variables
- `README.md` - Documentation
- `config/app.config` - Application configuration

### Bumpversion Entries
- `[bumpversion:file:./VERSION]`
- `[bumpversion:file:./README.md]`
- `[bumpversion:file:./_setup.py]`

### Environment Variables (in env.sh)
- `CONFIG` - Must be set to `config/app.config`
- `MODE` - Environment mode (development/production)

### Virtual Environment (selectable)
**Conda:**
- `environment.yml`

**UV:**
- `pyproject.toml`
- `uv.lock`
- `.python-version`
- Additional bumpversion entries for pyproject.toml and uv.lock

## Customization

### Adding Custom Checks

Edit `src/deploy_check/checks.py` to add your own checks:

```python
def check_custom_file(base_dir: Path) -> CheckItem:
    return CheckItem(
        id="custom_check",
        name="My Custom Check",
        passed=some_condition,
        can_fix=True,
        file_path="path/to/file",
        template_key="custom_template",
    )
```

### Adding File Templates

Edit `src/deploy_check/templates.py`:

```python
FILE_TEMPLATES = {
    # ... existing templates ...
    "custom_template": """Your template content here""",
}
```

## Development

```bash
# Clone the repo
git clone https://github.com/yourorg/deploy-checks.git
cd deploy-checks

# Install in dev mode
pip install -e ".[dev]"

# Run locally
python -m deploy_check.app

# Run linting
ruff check src/
```

## License

MIT
