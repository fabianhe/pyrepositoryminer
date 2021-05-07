#!/usr/bin/env /bin/bash

./mount-ramdisk-macos.sh 500000
pyrepositoryminer clone https://github.com/fabianhe/pyrepositoryminer /Volumes/RAMDisk/pyrepositoryminer.git
pyrepositoryminer branch --no-remote /Volumes/RAMDisk/pyrepositoryminer.git | pyrepositoryminer commits /Volumes/RAMDisk/pyrepositoryminer.git | pyrepositoryminer analyze /Volumes/RAMDisk/pyrepositoryminer.git raw halstead >> out.jsonl