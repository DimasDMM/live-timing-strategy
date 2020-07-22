<?php

declare(strict_types=1);

require realpath('./../vendor/autoload.php');

use CkmTiming\Utils\BasicContainer as Container;
use Slim\Factory\AppFactory;

// Create container
$container = new Container();
AppFactory::setContainer($container);

// Create Slim application
$app = AppFactory::create();

// Register middlewares, routes and services.
require realpath(__DIR__ . '/services.php');
require realpath(__DIR__ . '/dependencies.php');
require realpath(__DIR__ . '/routes.php');
require realpath(__DIR__ . '/middlewares.php');

// This middleware should be added last. It will not handle any exceptions/errors for middleware added after it.
require realpath(__DIR__ . '/errorHandlers.php');

// Run app
$app->run();
