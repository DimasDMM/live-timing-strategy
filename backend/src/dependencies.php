<?php

use CkmTiming\Helpers\ValidatorTypes;
use CkmTiming\Helpers\ValidatorRanges;
use CkmTiming\Storages\v1\Common\EventsIndexStorage;
use Psr\Container\ContainerInterface as Container;

// Storages
$callbacks = [
    'common' => [
        'events_index' => function () use ($container) { return new EventsIndexStorage($container); },
    ],
];
$container->set('storages', $callbacks);

// Validators
$container->set('validator_types', function (Container $container) { return new ValidatorTypes($container); });
$container->set('validator_ranges', function (Container $container) { return new ValidatorRanges($container); });
