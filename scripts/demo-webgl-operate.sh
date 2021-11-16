#!/usr/bin/env /bin/bash

mkdir "$(pwd)/data"
docker run -i -v "$(pwd)/data:/app/data" pyrepositoryminer clone "https://github.com/cginternals/webgl-operate.git" /app/data/webgl-operate/
docker run -i -v "$(pwd)/data:/app/data" pyrepositoryminer branch --no-remote /app/data/webgl-operate | \
    docker run -i -v "$(pwd)/data:/app/data" pyrepositoryminer commits /app/data/webgl-operate | \
    docker run -i -v "$(pwd)/data:/app/data" pyrepositoryminer analyze /app/data/webgl-operate loc linecount > webgl-operate-metrics.jsonl
