#!/bin/bash

SCRIPT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source ${SCRIPT_PATH}/environment-vars.sh

cd $SCRIPT_DIR/../../

# Build and run docker
source no_down=true
$SCRIPT_PATH/run.sh

fail=0

docker-compose -p $PROJECT_NAME exec -T api ./vendor/bin/phpcs --standard=PSR2 ./$1 --ignore=bootstrap --error-severity=1 --warning-severity=6
[ $? -gt 1 ] && fail=1

cd -

if [ $fail -eq 1 ]
then
  echo "There are some style warning\errors in the folder."
  exit 1
fi

echo "The style of the code is right!"

(exit 0)
