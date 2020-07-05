<?php
namespace CkmTiming\Enumerations;

final class Roles
{
    const ADMIN = 'admin';
    const USER = 'user';
    const BATCH = 'batch';

    public static function getConstants() : array
    {
        $oClass = new \ReflectionClass(__CLASS__);
        return $oClass->getConstants();
    }
}
