#!/bin/bash
docker build . --rm -t ericskang/db-jobs:migration

#docker login

docker push ericskang/db-jobs:migration
