__version__ = "0.8.0"

from typer import Typer

from pyrepositoryminer.commands import analyze, branch, clone, commits

app = Typer(help="Efficient Repository Mining in Python.")
app.command()(analyze)
app.command()(branch)
app.command()(clone)
app.command()(commits)

__all__ = ("app",)
