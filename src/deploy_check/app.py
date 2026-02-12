"""Main TUI application for deploy-check."""

import os
import subprocess
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Button, Header, Footer, Static, Label, RadioSet, RadioButton
from textual.binding import Binding

from .templates import FILE_TEMPLATES
from .checks import CheckItem, run_all_checks


class StatusIcon(Static):
    """A status icon widget."""

    def __init__(self, passed: bool, **kwargs):
        super().__init__(**kwargs)
        self.passed = passed

    def compose(self) -> ComposeResult:
        if self.passed:
            yield Label("✅", classes="status-pass")
        else:
            yield Label("❌", classes="status-fail")


class CheckRow(Horizontal):
    """A row displaying a single check item."""

    def __init__(self, check: CheckItem, **kwargs):
        super().__init__(**kwargs)
        self.check = check

    def compose(self) -> ComposeResult:
        icon = "✅" if self.check.passed else "❌"
        yield Label(icon, classes="status-icon")
        yield Label(self.check.name, classes="check-name")

        if not self.check.passed and self.check.can_fix:
            btn = Button("Create", id=f"fix_{self.check.id}", classes="create-btn")
            yield btn
        else:
            yield Label("", classes="spacer")


class DeployCheckApp(App):
    """Main application for deploy-check."""

    CSS = """
    Screen {
        background: $surface;
    }

    #main-container {
        padding: 1 2;
    }

    #title {
        text-align: center;
        text-style: bold;
        color: $primary;
        padding: 1;
    }

    #subtitle {
        text-align: center;
        color: $text-muted;
        padding-bottom: 1;
    }

    .section-title {
        text-style: bold;
        color: $secondary;
        padding: 1 0;
        border-bottom: solid $primary;
        margin-bottom: 1;
    }

    .check-row {
        height: 3;
        padding: 0 1;
        align: left middle;
    }

    .status-icon {
        width: 4;
    }

    .check-name {
        width: 1fr;
    }

    .create-btn {
        width: 12;
    }

    .spacer {
        width: 12;
    }

    .status-pass {
        color: green;
    }

    .status-fail {
        color: red;
    }

    #checks-container {
        height: auto;
        max-height: 60%;
        border: solid $primary;
        padding: 1;
        margin: 1 0;
    }

    #venv-section {
        height: auto;
        border: solid $primary;
        padding: 1;
        margin: 1 0;
    }

    #button-bar {
        height: 3;
        align: center middle;
        padding: 1;
    }

    #button-bar Button {
        margin: 0 1;
    }

    #status-bar {
        height: 3;
        align: center middle;
        padding: 1;
        border-top: solid $primary;
    }

    .success-message {
        color: green;
        text-style: bold;
    }

    .error-message {
        color: red;
        text-style: bold;
    }

    RadioSet {
        height: auto;
        padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("a", "create_all", "Create All"),
        Binding("l", "run_lint", "Run Linter"),
    ]

    def __init__(self, target_dir: str = "."):
        super().__init__()
        self.target_dir = Path(target_dir).resolve()
        self.checks: list[CheckItem] = []
        self.venv_type = "uv"

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main-container"):
            yield Label("🔍 Pre-Deployment Checker", id="title")
            yield Label(f"Directory: {self.target_dir}", id="subtitle")

            yield Label("📁 Required Files & Config", classes="section-title")
            with ScrollableContainer(id="checks-container"):
                yield from self._render_checks()

            yield Label("🐍 Virtual Environment Type", classes="section-title")
            with Container(id="venv-section"):
                with RadioSet(id="venv-radio"):
                    yield RadioButton("conda (environment.yml)", id="venv-conda")
                    yield RadioButton("uv (pyproject.toml + uv.lock)", id="venv-uv", value=True)
                    yield RadioButton("other (skip venv checks)", id="venv-other")

            with Horizontal(id="button-bar"):
                yield Button("Create All Missing", id="create-all", variant="primary")
                yield Button("Run Linter", id="run-lint", variant="default")
                yield Button("Refresh", id="refresh", variant="default")

            yield Label("", id="status-bar")

        yield Footer()

    def _render_checks(self):
        """Render all check rows."""
        self.checks = run_all_checks(self.target_dir, self.venv_type)
        for check in self.checks:
            yield CheckRow(check, classes="check-row")

    def _refresh_checks(self):
        """Refresh the checks display."""
        container = self.query_one("#checks-container")
        container.remove_children()
        self.checks = run_all_checks(self.target_dir, self.venv_type)
        for check in self.checks:
            container.mount(CheckRow(check, classes="check-row"))
        self._update_status()

    def _update_status(self):
        """Update the status bar."""
        failed = sum(1 for c in self.checks if not c.passed)
        status_bar = self.query_one("#status-bar", Label)
        if failed == 0:
            status_bar.update("✅ All checks passed!")
            status_bar.set_classes("success-message")
        else:
            status_bar.update(f"❌ {failed} check(s) failed")
            status_bar.set_classes("error-message")

    def on_mount(self):
        """Called when app is mounted."""
        self._update_status()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "create-all":
            self.action_create_all()
        elif button_id == "refresh":
            self.action_refresh()
        elif button_id == "run-lint":
            self.action_run_lint()
        elif button_id and button_id.startswith("fix_"):
            check_id = button_id[4:]
            self._fix_single(check_id)

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Handle venv type change."""
        radio_id = event.pressed.id
        if radio_id == "venv-conda":
            self.venv_type = "conda"
        elif radio_id == "venv-uv":
            self.venv_type = "uv"
        else:
            self.venv_type = "other"
        self._refresh_checks()

    def _fix_single(self, check_id: str):
        """Fix a single check by creating the file."""
        for check in self.checks:
            if check.id == check_id and check.can_fix:
                self._create_file(check)
                break
        self._refresh_checks()

    def _create_file(self, check: CheckItem):
        """Create a missing file from template."""
        if check.file_path and check.template_key:
            file_path = self.target_dir / check.file_path
            file_path.parent.mkdir(parents=True, exist_ok=True)

            template = FILE_TEMPLATES.get(check.template_key, "")
            file_path.write_text(template)

            # Make scripts executable
            if file_path.suffix == ".sh" or "bin/" in str(file_path):
                file_path.chmod(0o755)

    def action_refresh(self):
        """Refresh all checks."""
        self._refresh_checks()

    def action_create_all(self):
        """Create all missing files."""
        for check in self.checks:
            if not check.passed and check.can_fix:
                self._create_file(check)
        self._refresh_checks()

    def action_run_lint(self):
        """Run linter on the target directory."""
        status_bar = self.query_one("#status-bar", Label)
        status_bar.update("🔄 Running linter...")

        try:
            result = subprocess.run(
                ["ruff", "check", "."],
                cwd=self.target_dir,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                status_bar.update("✅ Linting passed!")
                status_bar.set_classes("success-message")
            else:
                status_bar.update("❌ Linting failed - check terminal output")
                status_bar.set_classes("error-message")
                self.log(result.stdout)
                self.log(result.stderr)
        except FileNotFoundError:
            status_bar.update("⚠️ Ruff not found - run: pip install ruff")
            status_bar.set_classes("error-message")


def main():
    """Entry point for the application."""
    import sys
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    app = DeployCheckApp(target_dir)
    app.run()


if __name__ == "__main__":
    main()
