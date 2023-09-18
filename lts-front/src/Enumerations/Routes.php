<?php
namespace LTS\Enumerations;

final class Routes
{
    // Initial routes
    const INDEX = '/';
    const TOKEN = '/token-validation';

    // Common event pages
    const EVENT_INDEX = '/event-index';
    const EVENT_CREATOR = '/event-creator';
    const EVENT_OVERVIEW = '/event/{event-name}';
    
    // SE pages
    const SE_KARTS_IN_BOX = '/event/{event-name}/karts-in-box';
    const SE_CONFIGURATION = '/event/{event-name}/configuration';

    public static function getConstants() : array
    {
        $oClass = new \ReflectionClass(__CLASS__);
        return $oClass->getConstants();
    }
}
