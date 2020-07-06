<?php
namespace CkmTiming\Middlewares;

use CkmTiming\Enumerations\Tables;
use Psr\Http\Message\ServerRequestInterface as Request;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Server\RequestHandlerInterface as RequestHandler;
use Slim\Exception\HttpBadRequestException;
use Slim\Routing\RouteContext;

class EventMiddleware extends AbstractMiddleware
{
    /**
     * @param Request $request
     * @param Response $response
     * @return Response
     */
    public function __invoke(Request $request, RequestHandler $handler) : Response
    {
        $routeContext = RouteContext::fromRequest($request);
        $route = $routeContext->getRoute();
        $eventName = $route->getArgument('event-name');

        $eventsIndexStorage = $this->container->get('storages')['common']['events_index']();
        $eventData = $eventsIndexStorage->getByName($eventName);

        if (empty($eventData)) {
            throw new HttpBadRequestException($request, 'Event does not exist.');
        }

        $this->container->set('event-index', $eventData);

        $response = $handler->handle($request);
        return $response;
    }
}
