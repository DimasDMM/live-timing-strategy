#!/bin/bash

SCRIPT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source ${SCRIPT_PATH}/environment-vars.sh

$SCRIPT_PATH/down.sh

cd $SCRIPT_PATH/../../
docker-compose -f docker-compose.yml -p $PROJECT_USER up -d --build
cd -

# Initialize database and import datasets
idocker database_${PROJECT_USER} bash ./code/wait-database.sh
idocker database_${PROJECT_USER} bash ./code/database-creation.sh
