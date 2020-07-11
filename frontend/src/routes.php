<?php

use CkmTiming\Controllers\v1\OverviewController;
use CkmTiming\Controllers\v1\KartsInBoxController;
use CkmTiming\Controllers\v1\TokenValidationController;
use CkmTiming\Controllers\v1\TrafficPredictionController;
use CkmTiming\Middlewares\DefaultMiddleware;
use CkmTiming\Enumerations\Routes;
use Slim\Routing\RouteCollectorProxy;

$app->redirect(Routes::INDEX, Routes::TOKEN, 301);

$app->group('', function (RouteCollectorProxy $group) {
    // Initial pages
    $group->get(Routes::TOKEN, TokenValidationController::class . ':get');

    // Data pages
    $group->get(Routes::OVERVIEW, OverviewController::class . ':get');
    $group->get(Routes::TRAFFIC_PREDICTION, TrafficPredictionController::class . ':get');
    $group->get(Routes::KARTS_IN_BOX, KartsInBoxController::class . ':get');
})->add(new DefaultMiddleware());

