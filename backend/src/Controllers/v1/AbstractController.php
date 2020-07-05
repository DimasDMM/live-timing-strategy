<?php
namespace CkmTiming\Controllers\v1;

use Psr\Container\ContainerInterface as Container;
use Psr\Http\Message\ServerRequestInterface as Request;
use Psr\Http\Message\ResponseInterface as Response;
use Slim\Exception\HttpForbiddenException;

abstract class AbstractController
{
    /** @var Container */
    protected $container;

    /**
     * @param Container $container
     */
    public function __construct(Container $container)
    {
        $this->container = $container;
    }

    /**
     * @param Request $request
     * @param array $roles
     * @return void
     */
    protected function validateRole(Request $request, array $roles) : void
    {
        $data = $this->container->get('logged');
        if (!in_array($data['role'], $roles)) {
            throw new HttpForbiddenException($request, 'No permissions.');
        }
    }

    /**
     * @param Request $request
     * @return array
     */
    protected function getParsedBody(Request $request) : array
    {
        $content = $request->getParsedBody();
        return !empty($content) ? $content : json_decode(file_get_contents('php://input'), true);
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
    protected function buildJsonResponse(Request $request, Response $response, $data = null, $message = 'ok')
    {
        $responseData = [
            'message' => 'ok',
            'data' => $data,
        ];

        $response->getBody()->write(json_encode($responseData));
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
