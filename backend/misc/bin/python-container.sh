#!/bin/bash

SCRIPT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source ${SCRIPT_PATH}/environment-vars.sh

if [ $1 == 'crawler' ]
then
    idocker python_${PROJECT_USER} python code/code/crawler/se_timing.py
else
    idocker python_${PROJECT_USER} bash
fi
