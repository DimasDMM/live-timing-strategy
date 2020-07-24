<?php
namespace CkmTiming\Controllers\v1;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

class ConfigurationController extends AbstractController
{
    /**
     * @param Request $request
     * @param Response $response
     * @param array $args Optional
     * @return Response
     */
    public function get(Request $request, Response $response, array $args = []) : Response
    {
        $eventName = $args['event-name'];

        $viewParams = $this->getViewParams($request, $args);
        $viewParams['event_name'] = $eventName;

        $html = $this->view->render($response, 'configuration.html', $viewParams);
        return $html;
    }
}
