# pyrepositoryminer

[![CI workflow](https://github.com/fabianhe/pyrepositoryminer/actions/workflows/test.yaml/badge.svg)](https://github.com/fabianhe/pyrepositoryminer/actions/workflows/test.yaml)
[![PyPI Python version](https://img.shields.io/pypi/pyversions/pyrepositoryminer?color=000000)](https://pypi.org/project/pyrepositoryminer/)
[![PyPI package](https://img.shields.io/pypi/v/pyrepositoryminer?color=%23000)](https://pypi.org/project/pyrepositoryminer/)
[![Tokei](https://tokei.rs/b1/github/fabianhe/pyrepositoryminer)](https://tokei.rs)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI downloads](https://img.shields.io/pypi/dm/pyrepositoryminer?color=000000)](https://pypi.org/project/pyrepositoryminer/)

The pyrepositoryminer aims to be a **performant**, **extendable** and **useful** tool for analyzing (large) software repositories.

## Installation

Install it from [PyPI](https://pypi.org/project/pyrepositoryminer/):

```console
$ pip install pyrepositoryminer
```

### Requirements

**Python 3.9+**, libgit2 (e.g. `brew install libgit2` on macOS).

pyrepositoryminer builds on the work of [pygit2](https://github.com/libgit2/pygit2) for the interaction with git repository objects, [typer](https://github.com/tiangolo/typer) for the CLI, [radon](https://github.com/rubik/radon) for Python-specific metrics, and [uvloop](https://github.com/MagicStack/uvloop) for an alternative event loop.

## Contributing

Install [poetry](https://github.com/python-poetry/poetry):

```console
$ curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -
```

Install the dependencies:

```console
$ poetry install
```

Install the [pre-commit](https://github.com/pre-commit/pre-commit) hooks:

```console
$ pre-commit install
```
