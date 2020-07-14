<?php

declare(strict_types=1);

require realpath('./../vendor/autoload.php');

use DI\Container;
use Slim\Views\Twig;
use Slim\Factory\AppFactory;

// Create container
$container = new Container();
AppFactory::setContainer($container);

// Use Twig to manage views
$container->set('view', function() {
    return Twig::create(__DIR__ . '/../templates');
});

// Create Slim application
$app = AppFactory::create();

// Register middlewares, routes and services.
require realpath(__DIR__ . '/routes.php');
require realpath(__DIR__ . '/middlewares.php');

// This middleware should be added last. It will not handle any exceptions/errors for middleware added after it.
require realpath(__DIR__ . '/errorHandlers.php');

// Run app
$app->run();
