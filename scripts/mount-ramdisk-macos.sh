#!/usr/bin/env /bin/bash

# Pass the number of memory blocks (512 B on macOS)
#     2.000 ~ 1 MB usable
#   500.000 ~ 250 MB usable
# 2.000.000 ~ 1 GB usable

diskutil erasevolume HFS+ 'RAMDisk' `hdiutil attach -nobrowse -nomount ram://$1`