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
     * @param array $data Optional
     * @return mixed
     */
    protected function buildResponse(Request $request, Response $response, array $data = [])
    {
        $response->getBody()->write(json_encode($data));
        $response = $response
            //->withHeader('Access-Control-Allow-Origin', '*')
            //->withHeader('Access-Control-Allow-Methods', 'GET, POST, DELETE, PUT, PATCH, OPTIONS')
            //->withHeader('Access-Control-Allow-Headers', 'Content-Type, api_key, Authorization')
            ->withHeader('Content-type', 'application/json');
        
        return $response;
    }
}
