<?php
namespace CkmTiming\Enumerations;

final class Tables
{
    const API_TOKENS = 'api_tokens';

    public static function getConstants() : array
    {
        $oClass = new \ReflectionClass(__CLASS__);
        return $oClass->getConstants();
    }
}
