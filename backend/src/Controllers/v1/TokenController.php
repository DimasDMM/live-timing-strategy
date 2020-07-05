<?php
namespace CkmTiming\Controllers\v1;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

class TokenController extends AbstractController
{
    /**
     * @param Request $request
     * @param Response $response
     * @return Response
     */
    public function get(Request $request, Response $response) : Response
    {
        $data = $this->container->get('logged');
        return $this->buildJsonResponse(
            $request,
            $response,
            $data
        );
    }
}
