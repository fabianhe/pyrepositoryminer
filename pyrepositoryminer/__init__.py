from pygit2 import clone_repository
from typer import Typer

app = Typer()


@app.command()
def main(url: str):
    clone_repository(
        url,
        "tempdir.git",
    )


if __name__ == "__main__":
    app()
