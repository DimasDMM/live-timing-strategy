#!/bin/bash

SCRIPT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source ${SCRIPT_PATH}/environment-vars.sh

cd $SCRIPT_DIR/../../

idocker api_${PROJECT_USER} ./doc/bin/script.sh
