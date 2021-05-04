#!/usr/bin/env /bin/bash

# Pass the number of bytes

diskutil erasevolume HFS+ 'RAMDisk' `hdiutil attach -nobrowse -nomount ram://$1`