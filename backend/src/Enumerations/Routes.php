<?php
namespace CkmTiming\Enumerations;

final class Routes
{
    // Common endpoints
    const API_VERSION = '/v1';
    const HEALTH = '/health';
    const DOCUMENTATION = '/documentation';

    const TOKEN_VALIDATE = '/token/validate';
    const EVENT = '/events';
    const EVENT_NAME = '/events/{event-name}';

    // Endpoints of Santos Endurance events
    const SE_STATS = '/stats';
    const SE_STATS_NAME = '/stats/{stat-name}';
    const SE_TEAMS = '/teams';
    const SE_TEAMS_NAME = '/teams/{team-name}';
    const SE_TEAMS_DRIVER_NAME = '/teams/{team-name}/{driver-name}';
    const SE_TIMING_TEAM = '/timing/teams/{team-name}[/{limit}]';

    public static function getConstants() : array
    {
        $oClass = new \ReflectionClass(__CLASS__);
        return $oClass->getConstants();
    }
}
