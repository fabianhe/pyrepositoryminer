#!/usr/bin/env /bin/bash

# This demo works as follows:
# 1. A ramdisk with ~250 MB usable space is created and mounted
# 2. The pyrepositoryminer clones itself to the ramdisk
# 3. The pyrepositoryminer finds the local branches (master)
# 4. Based on the branches, the pyrepositoryminer finds the commits on these branches
# 5. For each commit, the raw and halstead metrics for Python files are computed
# 6. The output is written to out.jsonl for further analysis in another tool

# Please note that you should detach the ramdisk manually

./mount-ramdisk-macos.sh 500000
pyrepositoryminer clone https://github.com/fabianhe/pyrepositoryminer /Volumes/RAMDisk/pyrepositoryminer.git
pyrepositoryminer branch --no-remote /Volumes/RAMDisk/pyrepositoryminer.git | pyrepositoryminer commits /Volumes/RAMDisk/pyrepositoryminer.git | pyrepositoryminer analyze /Volumes/RAMDisk/pyrepositoryminer.git raw halstead >> out.jsonl