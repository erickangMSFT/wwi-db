#!/bin/bash
docker build . --rm -t ericskang/wwi-db:migration

docker rmi -f $(docker images -f "dangling=true" -q)

docker images