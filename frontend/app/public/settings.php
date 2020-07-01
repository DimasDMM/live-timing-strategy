<?php

return [
    // Slim settings
    'settings' => [
        'displayErrorDetails' => in_array(getenv('DEBUG_ERRORS') == 'yes'),
        // Only set this if you need access to route within middleware
        'determineRouteBeforeAppMiddleware' => true
    ]
];
