#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/ && pwd )"
ORIGIN="$DIR/../index.json";
DESTINATION="$DIR/../api-description.json";

if [ -n "$1" ];
then
    DESTINATION=$1;
fi

cd $DIR/

# Install Node js if needed
if ! [[ -x "$(command -v npm)" ]]; then
    curl -sL https://deb.nodesource.com/setup_8.x | bash - && apt-get install -y nodejs
    apt-get install -y npm
fi

npm install
node doc-builder $ORIGIN $DESTINATION
