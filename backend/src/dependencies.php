<?php

use CkmTiming\Helpers\EventCreator;
use CkmTiming\Helpers\ValidatorTypes;
use CkmTiming\Helpers\ValidatorRanges;
use CkmTiming\Storages\v1\Common\EventsIndexStorage;
use CkmTiming\Storages\v1\SantosEndurance\EventConfigStorage;
use Psr\Container\ContainerInterface as Container;

// Storages
$callbacks = [
    'common' => [
        'events_index' => function () use ($container) { return new EventsIndexStorage($container); },
    ],
    'santos_endurance' => [
        'event_config' => function () use ($container) { return new EventConfigStorage($container); },
    ],
];
$container->set('storages', $callbacks);

// Helpers
$container->set('validator_types', function (Container $container) { return new ValidatorTypes($container); });
$container->set('validator_ranges', function (Container $container) { return new ValidatorRanges($container); });
$container->set('event_creator', function (Container $container) { return new EventCreator($container); });
