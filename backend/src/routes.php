<?php

use CkmTiming\Controllers\v1\HealthController;
use CkmTiming\Controllers\v1\DocumentationController;
use CkmTiming\Controllers\v1\EventController;
use CkmTiming\Controllers\v1\SantosEndurance\DriversController;
use CkmTiming\Controllers\v1\SantosEndurance\StatsController;
use CkmTiming\Controllers\v1\SantosEndurance\TeamsController;
use CkmTiming\Controllers\v1\TokenController;
use CkmTiming\Middlewares\TokenMiddleware;
use CkmTiming\Enumerations\Routes;
use CkmTiming\Middlewares\EventMiddleware;
use Slim\Routing\RouteCollectorProxy;

$app->group(Routes::API_VERSION, function (RouteCollectorProxy $group) {
    $group->get(Routes::DOCUMENTATION, DocumentationController::class . ':get');
});

$app->group('', function (RouteCollectorProxy $group) {
    $group->get(Routes::HEALTH, HealthController::class . ':get');
    $group->get(Routes::TOKEN_VALIDATE, TokenController::class . ':get');

    $group->group(Routes::API_VERSION, function (RouteCollectorProxy $group) {
        global $container;

        $group->get(Routes::EVENT, EventController::class . ':get');
        $group->post(Routes::EVENT, EventController::class . ':post');

        $group->group(Routes::EVENT_NAME, function (RouteCollectorProxy $group) {
            // Santos Endurance endpoints
            $group->get(Routes::SE_STATS, StatsController::class . ':get');
            $group->get(Routes::SE_STATS_NAME, StatsController::class . ':getByName');
            $group->put(Routes::SE_STATS_NAME, StatsController::class . ':putByName');
            
            $group->get(Routes::SE_TEAMS, TeamsController::class . ':get');
            $group->post(Routes::SE_TEAMS, TeamsController::class . ':post');
            $group->get(Routes::SE_TEAMS_NAME, TeamsController::class . ':getByName');
            $group->put(Routes::SE_TEAMS_NAME, TeamsController::class . ':putByName');
            $group->get(Routes::SE_TEAMS_DRIVER_NAME, DriversController::class . ':getByName');
            $group->put(Routes::SE_TEAMS_DRIVER_NAME, DriversController::class . ':putByName');

            $group->get(Routes::SE_TIMING_TEAM, TimingController::class . ':getByTeamName');
        })->add(new EventMiddleware($container));
    });
})->add(new TokenMiddleware($container));
