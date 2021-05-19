# `pyrepositoryminer`

Efficient Repository Mining in Python.

**Usage**:

```console
$ pyrepositoryminer [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `analyze`: Analyze commits of a repository.
* `branch`: Get the branches of a repository.
* `clone`: Clone a repository to a path.
* `commits`: Get the commit ids of a repository.

## `pyrepositoryminer analyze`

Analyze commits of a repository.

**Usage**:

```console
$ pyrepositoryminer analyze [OPTIONS] REPOSITORY [METRICS]:[complexity|filecount|halstead|halstead_total|linelength|loc|maintainability|nesting|raw]...
```

**Arguments**:

* `REPOSITORY`: [required]
* `[METRICS]:[complexity|filecount|halstead|halstead_total|linelength|loc|maintainability|nesting|raw]...`

**Options**:

* `--commits FILENAME`
* `--workers INTEGER`: [default: 1]
* `--global-cache / --no-global-cache`: [default: False]
* `--help`: Show this message and exit.

## `pyrepositoryminer branch`

Get the branches of a repository.

**Usage**:

```console
$ pyrepositoryminer branch [OPTIONS] PATH
```

**Arguments**:

* `PATH`: [required]

**Options**:

* `--local / --no-local`: [default: True]
* `--remote / --no-remote`: [default: True]
* `--help`: Show this message and exit.

## `pyrepositoryminer clone`

Clone a repository to a path.

**Usage**:

```console
$ pyrepositoryminer clone [OPTIONS] URL PATH
```

**Arguments**:

* `URL`: [required]
* `PATH`: [required]

**Options**:

* `--help`: Show this message and exit.

## `pyrepositoryminer commits`

Get the commit ids of a repository.

**Usage**:

```console
$ pyrepositoryminer commits [OPTIONS] REPOSITORY
```

**Arguments**:

* `REPOSITORY`: The path to the repository.  [required]

**Options**:

* `--branches FILENAME`: The branches to pull the commits from.
* `--simplify-first-parent / --no-simplify-first-parent`: [default: True]
* `--drop-duplicates / --no-drop-duplicates`: [default: False]
* `--sort [topological|time]`
* `--sort-reverse / --no-sort-reverse`: [default: False]
* `--help`: Show this message and exit.
