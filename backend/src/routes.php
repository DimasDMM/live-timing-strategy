<?php

use CkmTiming\Controllers\v1\HealthController;
use CkmTiming\Controllers\v1\DocumentationController;
use CkmTiming\Middlewares\DefaultMiddleware;
use CkmTiming\Enumerations\Routes;
use Slim\Routing\RouteCollectorProxy;

$app->group('', function (RouteCollectorProxy $group) {
    $group->get(Routes::HEALTH, HealthController::class . ':get');

    $group->group(Routes::API_VERSION, function (RouteCollectorProxy $group) {
        $group->get(Routes::DOCUMENTATION, DocumentationController::class . ':get');
    });
})->add(new DefaultMiddleware());
