<?php
namespace CkmTiming\Controllers\v1\SantosEndurance;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Routing\RouteContext;

class EventStatsController extends AbstractSantosEnduranceController
{
    /**
     * @param Request $request
     * @param Response $response
     * @return Response
     */
    public function get(Request $request, Response $response) : Response
    {
        $eventIndex = $this->container->get('event-index');
        $tablesPrefix = $eventIndex['tables_prefix'];
        
        $eventStatsStorage = $this->container->get('storages')['santos_endurance']['event_stats']();
        $eventStatsStorage->setTablesPrefix($tablesPrefix);
        $data = $eventStatsStorage->getAll();

        return $this->buildJsonResponse(
            $request,
            $response,
            $data
        );
    }
    /**
     * @param Request $request
     * @param Response $response
     * @return Response
     */
    public function getByName(Request $request, Response $response) : Response
    {
        $eventIndex = $this->container->get('event-index');
        $tablesPrefix = $eventIndex['tables_prefix'];
        
        $routeContext = RouteContext::fromRequest($request);
        $route = $routeContext->getRoute();
        $statName = $route->getArgument('stat-name');
        
        $eventStatsStorage = $this->container->get('storages')['santos_endurance']['event_stats']();
        $eventStatsStorage->setTablesPrefix($tablesPrefix);
        $data = $eventStatsStorage->getByName($statName);

        return $this->buildJsonResponse(
            $request,
            $response,
            $data
        );
    }
}
