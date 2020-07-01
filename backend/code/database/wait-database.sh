#!/bin/bash

echo "Connecting to database..."
sleep 5

while ! mysqladmin ping --silent
do
    sleep 5
    echo "Retrying in 5 seconds..."
done

echo "Database is ready"
