<?php

use CkmTiming\Controllers\v1\HealthController;
use CkmTiming\Controllers\v1\DocumentationController;
use CkmTiming\Controllers\v1\EventController;
use CkmTiming\Controllers\v1\TokenController;
use CkmTiming\Middlewares\TokenMiddleware;
use CkmTiming\Enumerations\Routes;
use Slim\Routing\RouteCollectorProxy;

$app->group(Routes::API_VERSION, function (RouteCollectorProxy $group) {
    $group->get(Routes::DOCUMENTATION, DocumentationController::class . ':get');
});

$app->group('', function (RouteCollectorProxy $group) {
    $group->get(Routes::HEALTH, HealthController::class . ':get');
    $group->get(Routes::TOKEN_VALIDATE, TokenController::class . ':get');

    $group->group(Routes::API_VERSION, function (RouteCollectorProxy $group) {
        $group->get(Routes::EVENT, EventController::class . ':get');
        $group->post(Routes::EVENT, EventController::class . ':post');
    });
})->add(new TokenMiddleware($container));
