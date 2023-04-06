#!/bin/bash

echo "Connecting to database..."
sleep 5

echo "mysqladmin ping --host ${DB_HOST} --port ${DB_PORT} --silent"
while ! mysqladmin ping --host ${DB_HOST} --port ${DB_PORT}
do
    sleep 5
    echo "Retrying in 5 seconds..."
done

echo "Database is ready"
