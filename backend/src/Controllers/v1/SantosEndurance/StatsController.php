<?php
namespace CkmTiming\Controllers\v1\SantosEndurance;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Exception\HttpBadRequestException;
use Slim\Routing\RouteContext;

class StatsController extends AbstractSantosEnduranceController
{
    protected $validStatus = ['offline', 'online', 'error'];
    protected $validStages = ['classification', 'race'];

    /**
     * @param Request $request
     * @param Response $response
     * @return Response
     */
    public function get(Request $request, Response $response) : Response
    {
        $eventIndex = $this->container->get('event-index');
        $tablesPrefix = $eventIndex['tables_prefix'];
        
        $eventStatsStorage = $this->container->get('storages')['santos_endurance']['stats']();
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
        
        /** @var \CkmTiming\Storages\v1\SantosEndurance\StatsStorage $eventStatsStorage */
        $eventStatsStorage = $this->container->get('storages')['santos_endurance']['stats']();
        $eventStatsStorage->setTablesPrefix($tablesPrefix);
        $data = $eventStatsStorage->getByName($statName);

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
     * @throws HttpBadRequestException
     */
    public function putByName(Request $request, Response $response) : Response
    {
        $eventIndex = $this->container->get('event-index');
        $tablesPrefix = $eventIndex['tables_prefix'];
        
        $routeContext = RouteContext::fromRequest($request);
        $route = $routeContext->getRoute();
        $statName = $route->getArgument('stat-name');
        
        /** @var \CkmTiming\Storages\v1\SantosEndurance\StatsStorage $statsStorage */
        $eventStatsStorage = $this->container->get('storages')['santos_endurance']['stats']();
        $eventStatsStorage->setTablesPrefix($tablesPrefix);
        $stat = $eventStatsStorage->getByName($statName);

        if (empty($stat)) {
            throw new HttpBadRequestException($request, 'The stat does not exist.');
        }

        $data = $this->getParsedBody($request);
        $this->validatePutStatValue($request, $data, $statName);

        $eventStatsStorage->updateByName($statName, $data['value']);

        return $this->buildJsonResponse($request, $response);
    }

    /**
     * @param Request $request
     * @param array $stat
     * @param string $statName
     * @return void
     */
    protected function validatePutStatValue(Request $request, array $stat, string $statName) : void
    {
        /** @var \CkmTiming\Helpers\ValidatorTypes $validatorTypes */
        $validatorTypes = $this->container->get('validator_types')->setRequest($request);
        /** @var \CkmTiming\Helpers\ValidatorRanges $validatorRanges */
        $validatorRanges = $this->container->get('validator_ranges')->setRequest($request);

        // Value is set
        $validatorTypes->isNull('value', $stat['value'] ?? null);
        
        // Values has correct format
        switch ($statName) {
            case 'reference_time':
                $validatorTypes->isNumeric('reference_time', $stat['value']);
                break;
            case 'reference_current_offset':
                $validatorTypes->isNumeric('reference_current_offset', $stat['value']);
                break;
            case 'status':
                $validatorRanges->inArray('status', $stat['value'], $this->validStatus);
                break;
            case 'stage':
                $validatorRanges->inArray('stage', $stat['value'], $this->validStages);
                break;
            case 'remaining_event':
                $validatorTypes->isNumeric('remaining_event', $stat['value']);
                break;
        }
    }
}
