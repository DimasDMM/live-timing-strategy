<?php

use LTS\Controllers\v1\AuthController;
use LTS\Controllers\v1\CompetitionsIndexController;
use LTS\Controllers\v1\ConfigurationController;
use LTS\Controllers\v1\EventCreatorController;
use LTS\Controllers\v1\CompetitionsOverviewController;
use LTS\Controllers\v1\KartsInBoxController;
use LTS\Middlewares\DefaultMiddleware;
use LTS\Enumerations\Routes;
use Slim\Routing\RouteCollectorProxy;

$app->redirect(Routes::INDEX, Routes::AUTH, 301);

$app->group('', function (RouteCollectorProxy $group) {
    // Initial pages
    $group->get(Routes::AUTH, AuthController::class . ':get');
    
    // Common event pages
    $group->get(Routes::COMPETITIONS_INDEX, CompetitionsIndexController::class . ':get');
    $group->get(Routes::COMPETITIONS_CREATOR, EventCreatorController::class . ':get');
    $group->get(Routes::COMPETITIONS_OVERVIEW, CompetitionsOverviewController::class . ':get');

    // SE pages
    $group->get(Routes::SE_CONFIGURATION, ConfigurationController::class . ':get');
    $group->get(Routes::SE_KARTS_IN_BOX, KartsInBoxController::class . ':get');
})->add(new DefaultMiddleware());
