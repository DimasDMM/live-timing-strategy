<?php
namespace CkmTiming\Controllers\v1;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

class TrafficPredictionController extends AbstractController
{
    /**
     * @param Request $request
     * @param Response $response
     * @param array $args Optional
     * @return Response
     */
    public function get(Request $request, Response $response, array $args = []) : Response
    {
        $viewParams = $this->getViewParams($request, $args);

        $html = $this->view->render($response, 'traffic_prediction.html', $viewParams);
        return $html;
    }
}
