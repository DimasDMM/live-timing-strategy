<?php

/**
 * Add Error Handling Middleware
 *
 * @param bool $displayErrorDetails Should be set to false in production
 * @param bool $logErrors Parameter is passed to the default ErrorHandler
 * @param bool $logErrorDetails Display error details in error log
 *             which can be replaced by a callable of your choice.
 */
$errorMiddleware = $app->addErrorMiddleware(true, true, true);
$errorMiddleware->setDefaultErrorHandler($customErrorHandler);
