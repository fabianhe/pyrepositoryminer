from typer.testing import CliRunner

from pyrepositoryminer import app

runner = CliRunner()


def test_app_fails_without_arguments():
    result = runner.invoke(app)
    assert result.exit_code == 2
