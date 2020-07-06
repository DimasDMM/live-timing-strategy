#!/bin/bash

SCRIPT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source ${SCRIPT_PATH}/environment-vars.sh

cd $SCRIPT_DIR/../../

# Define local variables
container_name=${PROJECT_USER}_doc
api_host=$NGINX_HOST:$NGINX_PORT/$API_VERSION/documentation
api_doc_url=$API_HOST:$API_EXTERNAL_PORT/$API_VERSION/documentation
swagger_url=$SWAGGER_UI_HOST:$SWAGGER_UI_PORT

swagger_image=swaggerapi/swagger-ui:v3.20.4

# Setup docker container
docker pull $swagger_image

# Stop old containers
docker stop $container_name
docker rm $container_name

# Remove swagger-ui container without failing if container doesn't exist
docker ps -q --filter "name=$container_name" | grep -q . && docker rm -fv $container_name

# Note: 8080 is the internal port of Swagger
docker run -p $SWAGGER_UI_PORT:8080 -e API_URL=$api_doc_url -d --name $container_name $swagger_image

echo -e "\n$PROJECT_NAME API documentation:\n$swagger_url"
