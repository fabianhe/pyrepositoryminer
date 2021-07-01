#!/usr/bin/env /bin/bash

docker create -it --name mycontainer -v $1/:/repo.git myimage
docker start mycontainer
docker exec -i mycontainer sh -c 'pyrepositoryminer branch /repo.git |  pyrepositoryminer commits /repo.git | pyrepositoryminer analyze /repo.git'
docker stop mycontainer
docker rm mycontainer