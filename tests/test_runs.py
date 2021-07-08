from pytest import mark
from typer.testing import CliRunner

from pyrepositoryminer import app

runner = CliRunner()


def test_app_fails_without_arguments() -> None:
    result = runner.invoke(app)
    assert result.exit_code == 0
    assert "Usage:" in result.stdout
    assert "Options:" in result.stdout
    assert "Commands:" in result.stdout


@mark.parametrize("command", ["filecount", "loc"])
def test_command_fails_without_arguments(command: str) -> None:
    result = runner.invoke(app, command)
    assert result.exit_code == 2
