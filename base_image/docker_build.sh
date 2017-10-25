#!/bin/bash
docker build . --rm -t ericskang/db-jobs:base

#docker login

docker push ericskang/db-jobs:base
