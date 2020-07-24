<?php

use Doctrine\DBAL\DriverManager;

// Use persistent connection to speed-up code execution
$limit = 5;
$counter = 0;
while ($counter < $limit) {
    try {
        $dbh = new \PDO(
            'mysql:host=' . getenv('DB_HOST') . ';dbname=' . getenv('DB_DATABASE') . ';charset=utf8',
            getenv('DB_USER'),
            getenv('DB_PASS')
        );
        $dbh->setAttribute(\PDO::ATTR_PERSISTENT, true);
        break;
    } catch (Exception $e) {
        $counter++;
        if ($counter == $limit) {
            throw $e;
        }
    }
}

$connection = DriverManager::getConnection([
    'host' => getenv('DB_HOST'),
    'user' => getenv('DB_USER'),
    'password' => getenv('DB_PASS'),
    'dbname' => getenv('DB_DATABASE'),
    'pdo' => $dbh,
    'charset' => 'utf8',
]);
$container->set('db', $connection);
