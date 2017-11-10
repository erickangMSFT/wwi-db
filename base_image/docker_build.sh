#!/bin/bash
docker build . --rm -t ericskang/db-jobs:base

docker push ericskang/db-jobs:base
