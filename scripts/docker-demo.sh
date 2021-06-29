#!/usr/bin/env /bin/bash

docker create -it --name mycontainer -v $1/:/repo.git myimage
docker start mycontainer
docker exec -i mycontainer pyrepositoryminer branch /repo.git | docker exec -i mycontainer pyrepositoryminer commits --limit 1 /repo.git | docker exec -i mycontainer pyrepositoryminer analyze /repo.git
docker stop mycontainer
docker rm mycontainer