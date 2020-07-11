<?php
namespace CkmTiming\Enumerations;

final class Routes
{
    // Initial routes
    const INDEX = '/';
    const TOKEN = '/token-validation';

    // Data pages
    const CONFIGURATION = '/configuration';
    const KARTS_IN_BOX = '/karts-in-box';
    const OVERVIEW = '/overview';
    const TRAFFIC_PREDICTION = '/traffic-prediction';

    public static function getConstants() : array
    {
        $oClass = new \ReflectionClass(__CLASS__);
        return $oClass->getConstants();
    }
}
