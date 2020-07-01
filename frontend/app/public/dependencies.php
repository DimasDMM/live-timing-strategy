<?php

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Factory\AppFactory;

// Get app settings
$settings = require realpath(__DIR__ . '/settings.php');

// Create Slim application
$app = AppFactory::create($settings);

$container = $app->getContainer();
$container->set('view', function(\Psr\Container\ContainerInterface $container){
    return new \Slim\Views\Twig('');
});

// Register middlewares, routes and services.
require realpath(__DIR__ . '/routes.php');
require realpath(__DIR__ . '/services.php');
require realpath(__DIR__ . '/middlewares.php');

// This middleware should be added last. It will not handle any exceptions/errors for middleware added after it.
require realpath(__DIR__ . '/errorHandlers.php');
