"""Check definitions and validation logic."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import re


@dataclass
class CheckItem:
    """Represents a single check item."""

    id: str
    name: str
    passed: bool
    can_fix: bool = False
    file_path: Optional[str] = None
    template_key: Optional[str] = None
    message: Optional[str] = None


def check_file_exists(base_dir: Path, file_path: str, template_key: str = None) -> CheckItem:
    """Check if a required file exists."""
    full_path = base_dir / file_path
    exists = full_path.exists()

    return CheckItem(
        id=file_path.replace("/", "_").replace(".", "_"),
        name=file_path,
        passed=exists,
        can_fix=template_key is not None,
        file_path=file_path,
        template_key=template_key,
    )


def check_bumpversion_entry(base_dir: Path, entry: str) -> CheckItem:
    """Check if a bumpversion entry exists in .bumpversion.cfg."""
    cfg_path = base_dir / ".bumpversion.cfg"
    entry_id = entry.replace("[", "").replace("]", "").replace(":", "_").replace("/", "_").replace(".", "_")

    if not cfg_path.exists():
        return CheckItem(
            id=f"bump_{entry_id}",
            name=f"bumpversion: {entry}",
            passed=False,
            can_fix=False,
            message=".bumpversion.cfg not found",
        )

    content = cfg_path.read_text()
    exists = entry in content

    return CheckItem(
        id=f"bump_{entry_id}",
        name=f"bumpversion: {entry}",
        passed=exists,
        can_fix=False,  # Can't auto-fix bumpversion entries easily
        message=None if exists else f"Missing entry: {entry}",
    )


def check_env_variable(base_dir: Path, var_name: str) -> CheckItem:
    """Check if env.sh contains a specific variable."""
    env_path = base_dir / "env.sh"

    if not env_path.exists():
        return CheckItem(
            id=f"env_{var_name}",
            name=f"env.sh: {var_name}",
            passed=False,
            can_fix=False,
            message="env.sh not found",
        )

    content = env_path.read_text()
    pattern = rf'^(export\s+)?{var_name}='
    exists = bool(re.search(pattern, content, re.MULTILINE))

    return CheckItem(
        id=f"env_{var_name}",
        name=f"env.sh: {var_name} variable",
        passed=exists,
        can_fix=False,
        message=None if exists else f"Missing {var_name} in env.sh",
    )


def check_config_value(base_dir: Path) -> CheckItem:
    """Check if CONFIG variable points to config/app.config."""
    env_path = base_dir / "env.sh"

    if not env_path.exists():
        return CheckItem(
            id="config_value",
            name="env.sh: CONFIG=config/app.config",
            passed=False,
            can_fix=False,
        )

    content = env_path.read_text()
    # Look for CONFIG="config/app.config" or CONFIG=config/app.config
    pattern = r'''CONFIG=["']?config/app\.config["']?'''
    exists = bool(re.search(pattern, content))

    return CheckItem(
        id="config_value",
        name="env.sh: CONFIG → config/app.config",
        passed=exists,
        can_fix=False,
    )


def run_all_checks(base_dir: Path, venv_type: str = "uv") -> list[CheckItem]:
    """Run all pre-deployment checks."""
    base_dir = Path(base_dir)
    checks = []

    # Required files
    file_checks = [
        ("VERSION", "VERSION"),
        (".bumpversion.cfg", "bumpversion_cfg"),
        ("_setup.py", "setup_py"),
        ("bin/entrypoint.sh", "entrypoint_sh"),
        ("env.sh", "env_sh"),
        ("README.md", "readme_md"),
        ("config/app.config", "app_config"),
    ]

    for file_path, template_key in file_checks:
        checks.append(check_file_exists(base_dir, file_path, template_key))

    # Bumpversion entries
    bumpversion_entries = [
        "[bumpversion:file:./VERSION]",
        "[bumpversion:file:./README.md]",
        "[bumpversion:file:./_setup.py]",
    ]

    for entry in bumpversion_entries:
        checks.append(check_bumpversion_entry(base_dir, entry))

    # Environment variables
    checks.append(check_env_variable(base_dir, "CONFIG"))
    checks.append(check_env_variable(base_dir, "MODE"))
    checks.append(check_config_value(base_dir))

    # Venv-specific checks
    if venv_type == "conda":
        checks.append(check_file_exists(base_dir, "environment.yml", "environment_yml"))
    elif venv_type == "uv":
        checks.append(check_file_exists(base_dir, "pyproject.toml", "pyproject_toml"))
        checks.append(check_file_exists(base_dir, "uv.lock", None))  # Can't auto-generate
        checks.append(check_file_exists(base_dir, ".python-version", "python_version"))
        checks.append(check_bumpversion_entry(base_dir, "[bumpversion:file:./pyproject.toml]"))
        checks.append(check_bumpversion_entry(base_dir, "[bumpversion:file:./uv.lock]"))

    return checks
