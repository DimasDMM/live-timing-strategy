<?php
namespace CkmTiming\Controllers\v1;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

class HealthController extends AbstractController
{
    /**
     * Check that the API is working
     *
     * @param Request $request
     * @param Response $response
     * @return Response
     */
    public function get(Request $request, Response $response) : Response
    {
        $data = array(
            'health' => 'OK',
            'params' => $request->getQueryParams(),
        );
        return $this->buildResponse(
            $request,
            $response,
            $data
        );
    }
}
