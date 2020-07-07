#!/bin/bash

mysql -e "SET GLOBAL time_zone = 'Europe/Madrid';"
mysql -e "SET NAMES utf8;"
mysql -e "DROP DATABASE IF EXISTS $DB_DATABASE;"
mysql -e "CREATE DATABASE $DB_DATABASE CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql $DB_DATABASE < /bin/init_database/templates/initial_tables.sql

echo "Database has been initialized correctly"
