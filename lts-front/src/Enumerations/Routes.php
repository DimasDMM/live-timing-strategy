<?php
namespace LTS\Enumerations;

final class Routes
{
    // Initial routes
    const INDEX = '/';
    const AUTH = '/auth';

    // Common event pages
    const COMPETITIONS_INDEX = '/competitions-index';
    const COMPETITIONS_CREATOR = '/competitions-creator';
    const COMPETITIONS_OVERVIEW = '/competitions/{competition-code}';
    
    // SE pages
    const SE_KARTS_IN_BOX = '/competitions/{competition-code}/karts-in-box';
    const SE_CONFIGURATION = '/competitions/{competition-code}/configuration';

    public static function getConstants() : array
    {
        $oClass = new \ReflectionClass(__CLASS__);
        return $oClass->getConstants();
    }
}
