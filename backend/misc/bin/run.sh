#!/bin/bash

SCRIPT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source ${SCRIPT_PATH}/environment-vars.sh

if [ -z ${no_down} ] && [ "$no_down" = true ]
then
    $SCRIPT_PATH/down.sh
fi

cd $SCRIPT_PATH/../../
docker-compose -f docker-compose.yml -p $PROJECT_USER up -d --build
cd -

# Initialize database and import datasets
idocker api_${PROJECT_USER} bash ./misc/dockerfiles/php/container-dependencies.sh
idocker database_${PROJECT_USER} bash ./bin/init_database/wait-database.sh
idocker database_${PROJECT_USER} bash ./bin/init_database/database-creation.sh
