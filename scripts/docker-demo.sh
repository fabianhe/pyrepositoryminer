#!/usr/bin/env /bin/bash

docker build . -t myimage && docker run --env-file .env -v $1/:/repo.git --rm myimage sh -c 'pyrepositoryminer branch /repo.git |  pyrepositoryminer commits /repo.git | pyrepositoryminer analyze /repo.git'