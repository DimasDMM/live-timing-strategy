<?php
namespace CkmTiming\Middlewares;

use CkmTiming\Enumerations\Tables;
use Psr\Http\Message\ServerRequestInterface as Request;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Server\RequestHandlerInterface as RequestHandler;
use Slim\Exception\HttpUnauthorizedException;

class TokenMiddleware extends AbstractMiddleware
{
    const HEADER_TOKEN = 'X-Request-Id';

    /**
     * @param Request $request
     * @param Response $response
     * @return Response
     */
    public function __invoke(Request $request, RequestHandler $handler) : Response
    {
        $headers = $request->getHeaders();
        if (!isset($headers[self::HEADER_TOKEN])) {
            throw new HttpUnauthorizedException($request, 'Empty header ' . self::HEADER_TOKEN . '.');
        }

        $tokenData = $this->getTokenData($headers[self::HEADER_TOKEN][0]);
        if (empty($tokenData)) {
            throw new HttpUnauthorizedException($request, 'Token in ' . self::HEADER_TOKEN . ' not valid.');
        }

        $this->container->set('logged', $tokenData);

        $response = $handler->handle($request);
        return $response;
    }

    /**
     * @param string $token
     * @return array
     */
    protected function getTokenData(string $token) : array
    {
        $connection = $this->container->get('db');
        $query = "
            SELECT at.token, at.name, at.role
            FROM " . Tables::API_TOKENS . " at
            WHERE token = :token";

        $params = [':token' => $token];
        $results = $connection->executeQuery($query, $params)->fetch();

        return $results ?? [];
    }
}
