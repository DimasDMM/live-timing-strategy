<?php

use Doctrine\DBAL\DriverManager;

$connection = DriverManager::getConnection([
    'host' => getenv('DB_HOST'),
    'user' => getenv('DB_USER'),
    'password' => getenv('DB_PASS'),
    'dbname' => getenv('DB_DATABASE'),
    'driver' => 'pdo_mysql',
    'charset' => 'utf8',
]);
$container->set('db', $connection);
