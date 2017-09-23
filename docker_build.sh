#!/bin/bash
docker build . --rm -t ericskang/db-jobs:version-alpine

docker rmi -f $(docker images -f "dangling=true" -q)

docker login

docker push ericskang/db-jobs:version-alpine

