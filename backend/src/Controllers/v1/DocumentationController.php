<?php
namespace CkmTiming\Controllers\v1;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

class DocumentationController extends AbstractController
{
    const API_DOC_PATH = __DIR__ . '/../../../doc/api-description.yaml';

    /**
     * Get the yml documentation of the API
     *
     * @param Request $request
     * @param Response $response
     * @return Response
     */
    public function get(Request $request, Response $response) : Response
    {
        $data = file_get_contents(self::API_DOC_PATH);
        return $this->buildYamlResponse(
            $request,
            $response,
            $data
        );
    }
}
