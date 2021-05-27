#!/usr/bin/env /bin/bash

echo "How many commits are on all local branches?"
pyrepositoryminer branch $1 --no-remote | pyrepositoryminer commits $1 | wc -l

echo "Iterate all commits, no metrics:"
time (pyrepositoryminer branch $1 --no-remote | pyrepositoryminer commits $1 | pyrepositoryminer analyze $1 --workers 1 >> /dev/null)

echo "Iterate all commits, no metrics (4 workers):"
time (pyrepositoryminer branch $1 --no-remote | pyrepositoryminer commits $1 | pyrepositoryminer analyze $1 --workers 4 >> /dev/null)

echo "Filecount, 10000 commits:"
time (pyrepositoryminer branch $1 --no-remote | pyrepositoryminer commits $1 | head -10000 | pyrepositoryminer analyze $1 filecount --workers 1 >> /dev/null)

echo "Filecount, 10000 commits (4 workers):"
time (pyrepositoryminer branch $1 --no-remote | pyrepositoryminer commits $1 | head -10000 | pyrepositoryminer analyze $1 filecount --workers 4 >> /dev/null)

echo "Linecount, 25 commits:"
time (pyrepositoryminer branch $1 --no-remote | pyrepositoryminer commits $1 | head -25 | pyrepositoryminer analyze $1 linecount --workers 1 >> /dev/null)

echo "Linecount, 25 commits (4 workers):"
time (pyrepositoryminer branch $1 --no-remote | pyrepositoryminer commits $1 | head -25 | pyrepositoryminer analyze $1 linecount --workers 4 >> /dev/null)

echo "Halstead, 1000 commits:"
time (pyrepositoryminer branch $1 --no-remote | pyrepositoryminer commits $1 | head -1000 | pyrepositoryminer analyze $1 halstead --workers 1 >> /dev/null)

echo "Halstead, 1000 commits (4 workers):"
time (pyrepositoryminer branch $1 --no-remote | pyrepositoryminer commits $1 | head -1000 | pyrepositoryminer analyze $1 halstead --workers 4 >> /dev/null)