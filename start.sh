#!/bin/bash

# start container-framework
docker build -f Dockerfile -t jupyter-pathling .
docker-compose -f docker-compose.dev.yml up -d

# check logs of bunsen container for getting URL
docker exec -it jupyter-pathling bash -c "python work/kafka_stream_con.py"

# check logs of pathling container for getting URL
# docker logs -f jupyter-pathling