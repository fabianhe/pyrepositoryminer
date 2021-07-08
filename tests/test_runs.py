from pytest import mark
from typer.testing import CliRunner

from pyrepositoryminer import app

runner = CliRunner()

COMMANDS = ("analyze", "branch", "clone", "commits")


def test_cli_initializes() -> None:
    result = runner.invoke(app)
    assert result.exit_code == 0
    assert "Usage:" in result.stdout
    assert "Options:" in result.stdout
    assert "Commands:" in result.stdout
    commands = tuple(
        sorted(
            command.strip().split()[0]
            for command in result.stdout[result.stdout.find("Commands:") :].split("\n")[
                1:-1
            ]
        )
    )
    assert commands == COMMANDS


@mark.parametrize("command", COMMANDS)
def test_command_initializes(command: str) -> None:
    result = runner.invoke(app, (command, "--help"))
    assert result.exit_code == 0
    assert "Usage:" in result.stdout
    assert "Arguments:" in result.stdout
    assert "Options:" in result.stdout
