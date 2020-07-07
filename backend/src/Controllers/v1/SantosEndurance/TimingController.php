<?php
namespace CkmTiming\Controllers\v1\SantosEndurance;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Exception\HttpBadRequestException;
use Slim\Routing\RouteContext;

class TimingController extends AbstractSantosEnduranceController
{
    /**
     * @param Request $request
     * @param Response $response
     * @return Response
     */
    public function getByTeamName(Request $request, Response $response) : Response
    {
        $eventIndex = $this->container->get('event-index');
        $tablesPrefix = $eventIndex['tables_prefix'];
        
        $routeContext = RouteContext::fromRequest($request);
        $route = $routeContext->getRoute();
        $teamName = $route->getArgument('team-name');
        $limit = $route->getArgument('limit');

        $this->validateLimit($request, $limit);
        
        $timingStorage = $this->container->get('storages')['santos_endurance']['timing']();
        $timingStorage->setTablesPrefix($tablesPrefix);
        $data = $timingStorage->getByTeamName($teamName, $limit);

        // Cast integer and boolean values
        $data['position'] = (int)$data['position'];
        $data['team_number'] = (int)$data['team_number'];
        $data['team_reference_time_offset'] = (int)$data['team_reference_time_offset'];
        $data['driver_reference_time_offset'] = (int)$data['driver_reference_time_offset'];
        $data['driver_driving_time'] = (int)$data['driver_driving_time'];
        $data['lap'] = (int)$data['lap'];
        $data['gap'] = (int)$data['gap'];
        $data['number_stops'] = (int)$data['number_stops'];
        $data['is_stop'] = (bool)$data['is_stop'];

        return $this->buildJsonResponse(
            $request,
            $response,
            $data
        );
    }

    /**
     * @param Request $request
     * @param mixed $limit
     * @return void
     */
    protected function validateLimit(Request $request, $limit) : void
    {
        $validatorTypes = $this->container->get('validator_types')->setRequest($request);
        $validatorTypes->isNumeric('limit', $limit);
    }
}
