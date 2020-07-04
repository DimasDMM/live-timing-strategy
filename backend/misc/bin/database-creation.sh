#!/bin/bash

mysql -e "SET GLOBAL time_zone = 'Europe/Madrid';"
mysql -e "DROP DATABASE IF EXISTS $DB_DATABASE;"
mysql -e "CREATE DATABASE $DB_DATABASE CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

echo "Database has been initialized correctly"