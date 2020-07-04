<?php
namespace CkmTiming\Enumerations;

final class Routes
{
    const API_VERSION = '/v1';
    const HEALTH = '/health';
    const DOCUMENTATION = '/documentation';

    public static function getConstants() : array
    {
        $oClass = new \ReflectionClass(__CLASS__);
        return $oClass->getConstants();
    }
}
