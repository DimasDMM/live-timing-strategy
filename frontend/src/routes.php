<?php

use CkmTiming\Controllers\v1\HomeController;
use CkmTiming\Controllers\v1\TrafficPredictionController;
use CkmTiming\Middlewares\DefaultMiddleware;
use CkmTiming\Enumerations\Routes;
use Slim\Routing\RouteCollectorProxy;

$app->group('', function (RouteCollectorProxy $group) {
    $group->get(Routes::TRAFFIC_PREDICTION, TrafficPredictionController::class . ':get');
    $group->get(Routes::HOME, HomeController::class . ':get');
})->add(new DefaultMiddleware());

