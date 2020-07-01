<?php

use Slim\Middleware\ContentLengthMiddleware;

$contentLengthMiddleware = new ContentLengthMiddleware();
$app->add($contentLengthMiddleware);
