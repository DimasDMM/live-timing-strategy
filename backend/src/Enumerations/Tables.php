<?php
namespace CkmTiming\Enumerations;

final class Tables
{
    const EVENTS_INDEX = 'events_index';
    const API_TOKENS = 'api_tokens';

    // Santos Endurance
    const SE_DRIVERS = '_drivers';
    const SE_KARTS_IN = '_karts_in';
    const SE_KARTS_OUT = '_karts_out';
    const SE_KARTS_PROBS = '_karts_probs';
    const SE_EVENT_CONFIG = '_event_config';
    const SE_EVENT_STATS = '_event_stats';
    const SE_TIMING_HISTORIC = '_timing_historic';
    const SE_TEAMS = '_teams';

    public static function getConstants() : array
    {
        $oClass = new \ReflectionClass(__CLASS__);
        return $oClass->getConstants();
    }
}
