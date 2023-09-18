<?php
namespace LTS\Middlewares;

use Psr\Http\Message\ServerRequestInterface as Request;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Server\RequestHandlerInterface as RequestHandler;

class DefaultMiddleware
{
    /**
     * @param Request $request
     * @param Response $response
     * @param callable $next Next middleware Optional
     * @return Response
     */
    public function __invoke(Request $request, RequestHandler $handler) : Response
    {
        return $handler->handle($request);
    }
}
