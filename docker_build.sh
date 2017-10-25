#!/bin/bash
docker build . --rm -t ericskang/db-jobs:migration

docker push ericskang/db-jobs:migration
