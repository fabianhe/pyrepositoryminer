#!/usr/bin/env /bin/bash

# Tests are run using [hyperfine](https://github.com/sharkdp/hyperfine).
# If not explicitly mentioned, they are run on RAMDisk.

hyperfine --warmup 1 --runs 3 --export-json out1.json --parameter-list repo numpy.git,pandas.git,matplotlib.git,tensorflow.git 'pyrepositoryminer branch --no-remote {repo} | pyrepositoryminer commits {repo} | wc -l'

hyperfine --warmup 1 --runs 3 --export-json out2.json --parameter-list repo numpy.git,pandas.git,matplotlib.git,tensorflow.git --parameter-list workers 1,4 'pyrepositoryminer branch --no-remote {repo} | pyrepositoryminer commits {repo} | pyrepositoryminer analyze {repo} --workers {workers}'

hyperfine --warmup 1 --runs 3 --export-json out3.json --parameter-list repo numpy.git,pandas.git,matplotlib.git,tensorflow.git --parameter-list workers 1,4 'pyrepositoryminer branch --no-remote {repo} | pyrepositoryminer commits --limit 1000 {repo} | pyrepositoryminer analyze {repo} filecount --workers {workers}'

hyperfine --warmup 1 --runs 3 --export-json out4.json --parameter-list repo numpy.git,pandas.git,matplotlib.git,tensorflow.git --parameter-list workers 1,4 'pyrepositoryminer branch --no-remote {repo} | pyrepositoryminer commits --limit 100 {repo} | pyrepositoryminer analyze {repo} filecount --workers {workers} --global-cache'

# Run on disk, not RAMDisk
hyperfine --warmup 1 --runs 3 --export-json ~/Repositories/pyrepositoryminer/measurements/out5.json --parameter-list repo numpy.git,pandas.git,matplotlib.git,tensorflow.git --parameter-list workers 1,4 'pyrepositoryminer branch --no-remote {repo} | pyrepositoryminer commits --limit 1000 {repo} | pyrepositoryminer analyze {repo} filecount --workers {workers}'

hyperfine --warmup 1 --runs 3 --export-json out6.json --parameter-list repo numpy.git,pandas.git,matplotlib.git,tensorflow.git --parameter-list workers 1,4 'pyrepositoryminer branch --no-remote {repo} | pyrepositoryminer commits --limit 5 {repo} | pyrepositoryminer analyze {repo} linecount --workers {workers}'

# Run for each repo
pyrepositoryminer branch --no-remote $1 | pyrepositoryminer commits --limit 5 $1 | pyrepositoryminer analyze $1 filecount linecount >> $1.jsonl
