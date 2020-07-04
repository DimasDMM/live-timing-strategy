<?php
namespace CkmTiming\Controllers\v1;

use Psr\Container\ContainerInterface;
use Psr\Http\Message\ServerRequestInterface as Request;
use Psr\Http\Message\ResponseInterface as Response;

abstract class AbstractController
{
    /** @var ContainerInterface */
    protected $container;

    /**
     * @param ContainerInterface $c
     */
    public function __construct(ContainerInterface $c)
    {
        $this->container = $c;
    }

    /**
     * @param Request $request
     * @param Response $response
     * @param mixed $data Optional
     * @return mixed
     */
    protected function buildResponse(Request $request, Response $response, $data = null)
    {
        return $this->buildJsonResponse($request, $response, $data);
    }

    /**
     * @param Request $request
     * @param Response $response
     * @param mixed $data Optional
     * @return mixed
     */
    protected function buildJsonResponse(Request $request, Response $response, $data = null)
    {
        $response->getBody()->write(json_encode($data));
        $response = $response->withHeader('Content-type', 'application/json');
        
        return $response;
    }

    /**
     * @param Request $request
     * @param Response $response
     * @param mixed $data Optional
     * @return mixed
     */
    protected function buildYamlResponse(Request $request, Response $response, $data = null)
    {
        $response->getBody()->write($data);
        $response = $response->withHeader('Content-type', 'text/yaml');
        
        return $response;
    }
}
