<?php

use Slim\Middleware\ContentLengthMiddleware;
use Slim\Views\TwigMiddleware;

$contentLengthMiddleware = new ContentLengthMiddleware();
$app->add($contentLengthMiddleware);

$app->add(TwigMiddleware::createFromContainer($app));
