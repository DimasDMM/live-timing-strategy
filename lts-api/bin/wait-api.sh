#!/bin/bash

echo "Connecting to API REST..."

echo "curl --silent $API_LTS/v1/health"
while true
do
    response=$(curl --silent ${API_LTS}/v1/health | head -1)
    echo "- Response: $response"
    if [ $response = "{\"status\":\"ok\"}" ]
    then
        break
    fi

    sleep 5
    echo "Retrying in 5 seconds..."
done

echo "API REST is ready"
