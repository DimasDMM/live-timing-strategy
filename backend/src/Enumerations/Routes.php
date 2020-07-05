<?php
namespace CkmTiming\Enumerations;

final class Routes
{
    const API_VERSION = '/v1';
    const HEALTH = '/health';
    const DOCUMENTATION = '/documentation';

    const VALIDATE_TOKEN = '/validate-token';
    
    const EVENT = '/event';

    public static function getConstants() : array
    {
        $oClass = new \ReflectionClass(__CLASS__);
        return $oClass->getConstants();
    }
}
