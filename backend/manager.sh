#!/bin/bash

MANAGER_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $MANAGER_DIR
case $1 in
  docker:run)
    ${MANAGER_DIR}/misc/bin/run.sh
    ;;
  docker:down)
    ${MANAGER_DIR}/misc/bin/down.sh
    ;;
  doc:build)
    ${MANAGER_DIR}/misc/bin/doc-build.sh
    ;;
  doc:ui)
    ${MANAGER_DIR}/misc/bin/doc-ui.sh
    ;;
  code:style)
    ${MANAGER_DIR}/misc/bin/code-style.sh -p
    ;;
  python)
    ${MANAGER_DIR}/misc/bin/python-container.sh
    ;;
  *)
    echo "Error: The command does not exist!!"
    exit 1
    ;;
esac
