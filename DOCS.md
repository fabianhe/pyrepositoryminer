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

Either provide the commit ids to analyze on stdin or as a file argument.

**Usage**:

```console
$ pyrepositoryminer analyze [OPTIONS] REPOSITORY [COMMITS] [METRICS]:[blobcount|complexity|halstead|linecount|linelength|loc|maintainability|nesting|pylinecount|raw]...
```

**Arguments**:

* `REPOSITORY`: The path to the bare repository.  [required]
* `[COMMITS]`: The newline-separated input file of commit ids. Commit ids are read from stdin if this is not passed.  [default: -]
* `[METRICS]:[blobcount|complexity|halstead|linecount|linelength|loc|maintainability|nesting|pylinecount|raw]...`

**Options**:

* `--workers INTEGER`: [default: 1]
* `--help`: Show this message and exit.

## `pyrepositoryminer branch`

Get the branches of a repository.

**Usage**:

```console
$ pyrepositoryminer branch [OPTIONS] REPOSITORY
```

**Arguments**:

* `REPOSITORY`: The path to the bare repository.  [required]

**Options**:

* `--local / --no-local`: [default: True]
* `--remote / --no-remote`: [default: False]
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

Either provide the branches to get the commit ids from on stdin or as a file argument.

**Usage**:

```console
$ pyrepositoryminer commits [OPTIONS] REPOSITORY [BRANCHES]
```

**Arguments**:

* `REPOSITORY`: The path to the bare repository.  [required]
* `[BRANCHES]`: The newline-separated input file of branches to pull the commits from. Branches are read from stdin if this is not passed.  [default: -]

**Options**:

* `--simplify-first-parent / --no-simplify-first-parent`: [default: True]
* `--drop-duplicates / --no-drop-duplicates`: [default: False]
* `--sort [topological|time|none]`: [default: topological]
* `--sort-reverse / --no-sort-reverse`: [default: True]
* `--limit INTEGER`
* `--help`: Show this message and exit.
