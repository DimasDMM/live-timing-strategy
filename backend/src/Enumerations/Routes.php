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
    const EVENT_SE_STATS = '/stats';

    public static function getConstants() : array
    {
        $oClass = new \ReflectionClass(__CLASS__);
        return $oClass->getConstants();
    }
}
