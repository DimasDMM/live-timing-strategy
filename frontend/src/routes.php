<?php

use CkmTiming\Controllers\v1\EventCreatorController;
use CkmTiming\Controllers\v1\EventIndexController;
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
    
    // Common event pages
    $group->get(Routes::EVENT_INDEX, EventIndexController::class . ':get');
    $group->get(Routes::EVENT_CREATOR, EventCreatorController::class . ':get');
    $group->get(Routes::EVENT_OVERVIEW, OverviewController::class . ':get');

    // SE pages
    $group->get(Routes::SE_TRAFFIC_PREDICTION, TrafficPredictionController::class . ':get');
    $group->get(Routes::SE_KARTS_IN_BOX, KartsInBoxController::class . ':get');
})->add(new DefaultMiddleware());
