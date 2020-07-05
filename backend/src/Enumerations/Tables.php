<?php
namespace CkmTiming\Enumerations;

final class Tables
{
    const EVENTS_INDEX = 'events_index';
    const API_TOKENS = 'api_tokens';

    public static function getConstants() : array
    {
        $oClass = new \ReflectionClass(__CLASS__);
        return $oClass->getConstants();
    }
}
