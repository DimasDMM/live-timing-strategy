<?php
namespace CkmTiming\Enumerations;

final class Tables
{
    const EVENTS_INDEX = 'events_index';
    const API_TOKENS = 'api_tokens';

    // Santos Endurance
    const SE_EVENT_CONFIG = '_event_config';
    const SE_EVENT_STATS = '_event_stats';

    public static function getConstants() : array
    {
        $oClass = new \ReflectionClass(__CLASS__);
        return $oClass->getConstants();
    }
}
