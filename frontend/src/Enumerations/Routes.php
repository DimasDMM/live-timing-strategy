<?php
namespace CkmTiming\Enumerations;

final class Routes
{
    const HOME = '/';
    const KARTS_IN_BOX = '/karts-in-box';
    const TRAFFIC_PREDICTION = '/traffic-prediction';
    const CONFIGURATION = '/configuration';

    public static function getConstants() : array
    {
        $oClass = new \ReflectionClass(__CLASS__);
        return $oClass->getConstants();
    }
}
