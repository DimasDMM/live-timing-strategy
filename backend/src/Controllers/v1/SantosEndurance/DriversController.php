<?php
namespace CkmTiming\Controllers\v1\SantosEndurance;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Exception\HttpBadRequestException;
use Slim\Routing\RouteContext;

class DriversController extends AbstractSantosEnduranceController
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
        
        $routeContext = RouteContext::fromRequest($request);
        $route = $routeContext->getRoute();
        $teamName = $route->getArgument('team-name');
        $driverName = $route->getArgument('driver-name');

        /** @var \CkmTiming\Storages\v1\SantosEndurance\TeamsStorage $teamsStorage */
        $teamsStorage = $this->container->get('storages')['santos_endurance']['teams']();
        $teamsStorage->setTablesPrefix($tablesPrefix);
        $data = $teamsStorage->getByName($teamName);
        $teamId = $data['id'];

        /** @var \CkmTiming\Storages\v1\SantosEndurance\DriversStorage $driversStorage */
        $driversStorage = $this->container->get('storages')['santos_endurance']['drivers']();
        $driversStorage->setTablesPrefix($tablesPrefix);
        $data = $driversStorage->getByName($driverName, $teamId);

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
    public function post(Request $request, Response $response) : Response
    {
        $eventIndex = $this->container->get('event-index');
        $tablesPrefix = $eventIndex['tables_prefix'];
        
        $routeContext = RouteContext::fromRequest($request);
        $route = $routeContext->getRoute();
        $teamName = $route->getArgument('team-name');
        $driverName = $route->getArgument('driver-name');

        /** @var \CkmTiming\Storages\v1\SantosEndurance\TeamsStorage $teamsStorage */
        $teamsStorage = $this->container->get('storages')['santos_endurance']['teams']();
        $teamsStorage->setTablesPrefix($tablesPrefix);
        $teamData = $teamsStorage->getByName($teamName);
        
        if (empty($teamData)) {
            throw new HttpBadRequestException($request, 'The team does not exist.');
        }

        /** @var \CkmTiming\Storages\v1\SantosEndurance\DriversStorage $driversStorage */
        $driversStorage = $this->container->get('storages')['santos_endurance']['drivers']();
        $driversStorage->setTablesPrefix($tablesPrefix);
        $driverData = $driversStorage->getByName($driverName, $teamData['id']);

        if (!empty($driverData)) {
            throw new HttpBadRequestException($request, 'The driver already exists.');
        }

        // Add driver
        $driverData = [
            'team_id' => $teamData['id'],
            'name' => $driverName,
        ];
        $driversStorage->insert($driverData);

        return $this->buildJsonResponse($request, $response);
    }

    /**
     * @param Request $request
     * @param Response $response
     * @return Response
     * @throws HttpBadRequestException
     */
    public function put(Request $request, Response $response) : Response
    {
        $eventIndex = $this->container->get('event-index');
        $tablesPrefix = $eventIndex['tables_prefix'];
        
        $routeContext = RouteContext::fromRequest($request);
        $route = $routeContext->getRoute();
        $teamName = $route->getArgument('team-name');
        $driverName = $route->getArgument('driver-name');

        $data = $this->getParsedBody($request);
        $this->validatePutDriverValue($request, $data);

        /** @var \CkmTiming\Storages\v1\SantosEndurance\TeamsStorage $teamsStorage */
        $teamsStorage = $this->container->get('storages')['santos_endurance']['teams']();
        $teamsStorage->setTablesPrefix($tablesPrefix);
        $teamData = $teamsStorage->getByName($teamName);
        
        if (empty($teamData)) {
            throw new HttpBadRequestException($request, 'The team does not exist.');
        }

        /** @var \CkmTiming\Storages\v1\SantosEndurance\DriversStorage $driversStorage */
        $driversStorage = $this->container->get('storages')['santos_endurance']['drivers']();
        $driversStorage->setTablesPrefix($tablesPrefix);
        $driverData = $driversStorage->getByName($driverName, $teamData['id']);

        if (empty($driverData)) {
            throw new HttpBadRequestException($request, 'The driver does not exist.');
        }

        // Update driver
        $driversStorage->update($driverData['id'], $data);

        return $this->buildJsonResponse($request, $response);
    }

    /**
     * @param Request $request
     * @param array $driver
     * @return void
     */
    protected function validatePutDriverValue(Request $request, array $driver) : void
    {
        /** @var \CkmTiming\Helpers\ValidatorTypes $validatorTypes */
        $validatorTypes = $this->container->get('validator_types')->setRequest($request);
        /** @var \CkmTiming\Helpers\ValidatorRanges $validatorRanges */
        $validatorRanges = $this->container->get('validator_ranges')->setRequest($request);
        
        // Values has correct format
        if (isset($driver['reference_time_offset'])) {
            $validatorTypes->isInteger('reference_time_offset', $driver['reference_time_offset']);
            $validatorRanges->isPositiveNumber('reference_time_offset', $driver['reference_time_offset'], true);
        }
        if (isset($driver['driving_time'])) {
            $validatorTypes->isInteger('driving_time', $driver['driving_time']);
            $validatorRanges->isPositiveNumber('driving_time', $driver['driving_time'], true);
        }
    }
}
