#!/usr/bin/env /bin/bash

mkdir "$(pwd)/data"
docker run -i -v "$(pwd)/data:/app/data" pyrepositoryminer clone "https://github.com/cginternals/khrbinding-generator.git" /app/data/khrbinding-generator/
docker run -i -v "$(pwd)/data:/app/data" pyrepositoryminer branch --no-remote /app/data/khrbinding-generator | \
    docker run -i -v "$(pwd)/data:/app/data" pyrepositoryminer commits /app/data/khrbinding-generator | \
    docker run -i -v "$(pwd)/data:/app/data" pyrepositoryminer analyze /app/data/khrbinding-generator loc linecount halstead complexity > khrbinding-generator-metrics.jsonl
