<?php

use CkmTiming\Controllers\v1\HealthController;
use CkmTiming\Controllers\v1\DocumentationController;
use CkmTiming\Controllers\v1\TokenController;
use CkmTiming\Middlewares\TokenMiddleware;
use CkmTiming\Enumerations\Routes;
use Slim\Routing\RouteCollectorProxy;

$app->group('', function (RouteCollectorProxy $group) {
    $group->get(Routes::HEALTH, HealthController::class . ':get');
    $group->get(Routes::VALIDATE_TOKEN, TokenController::class . ':get');

    $group->group(Routes::API_VERSION, function (RouteCollectorProxy $group) {
        $group->get(Routes::DOCUMENTATION, DocumentationController::class . ':get');
    });
})->add(new TokenMiddleware($container));
