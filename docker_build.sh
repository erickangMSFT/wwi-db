#!/bin/bash
docker build . --rm -t sqlpass.azurecr.io/db-jobs:migration

docker push sqlpass.azurecr.io/db-jobs:migration
