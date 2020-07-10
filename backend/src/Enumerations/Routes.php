<?php
namespace CkmTiming\Enumerations;

final class Routes
{
    // Common endpoints
    const API_VERSION = '/v1';
    const DOCUMENTATION = '/documentation';

    const TOKEN_VALIDATE = '/token/validate';
    const EVENT = '/events';
    const EVENT_NAME = '/events/{event-name}';

    // Endpoints of Santos Endurance events
    const SE_CONFIGURATION = '/configuration';
    const SE_CONFIGURATION_NAME = '/configuration/{config-name}';
    const SE_HEALTH = '/health';
    const SE_HEALTH_NAME = '/health/{health-category}/{health-name}';
    const SE_KARTS_BOX_ACTION = '/karts-box/{kart-action}[/{limit}]';
    const SE_STATS = '/stats';
    const SE_STATS_NAME = '/stats/{stat-name}';
    const SE_TEAMS = '/teams';
    const SE_TEAMS_NAME = '/teams/{team-name}';
    const SE_TEAMS_DRIVER_NAME = '/teams/{team-name}/{driver-name}';
    const SE_TIMING = '/timing';
    const SE_TIMING_TEAM = '/timing/teams/{team-name}[/{limit}]';

    public static function getConstants() : array
    {
        $oClass = new \ReflectionClass(__CLASS__);
        return $oClass->getConstants();
    }
}
