<?php
namespace CkmTiming\Controllers\v1\SantosEndurance;

use Exception;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Exception\HttpBadRequestException;
use Slim\Routing\RouteContext;

class TeamsController extends AbstractSantosEnduranceController
{
    protected $validDriverAttributes = ['name' => true];

    /**
     * @param Request $request
     * @param Response $response
     * @return Response
     */
    public function get(Request $request, Response $response) : Response
    {
        $eventIndex = $this->container->get('event-index');
        $tablesPrefix = $eventIndex['tables_prefix'];
        
        $teamsStorage = $this->container->get('storages')['santos_endurance']['teams']();
        $teamsStorage->setTablesPrefix($tablesPrefix);
        $data = $teamsStorage->getAll();

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

        $data = $this->getParsedBody($request);
        $this->validatePostTeamValueTypes($request, $data);
        $this->validatePostTeamValueRanges($request, $data);

        /** @var \CkmTiming\Storages\v1\SantosEndurance\TeamsStorage $teamsStorage */
        $teamsStorage = $this->container->get('storages')['santos_endurance']['teams']();
        $teamsStorage->setTablesPrefix($tablesPrefix);

        /** @var \CkmTiming\Storages\v1\SantosEndurance\DriversStorage $driversStorage */
        $driversStorage = $this->container->get('storages')['santos_endurance']['drivers']();
        $driversStorage->setTablesPrefix($tablesPrefix);

        if (!empty($teamsStorage->getByName($data['name']))) {
            throw new HttpBadRequestException($request, 'The team already exists.');
        }

        // Start transaction
        $connection = $this->getConnection();
        $connection->beginTransaction();
        try {
            $row = [
                'name' => $data['name'],
                'number' => $data['number'],
                'reference_time_offset' => $data['reference_time_offset'],
            ];

            // Insert team
            $teamsStorage->insert($row);
            $teamId = $teamsStorage->getByName($data['name'])['id'];
            
            if (empty($teamId)) {
                throw new HttpBadRequestException($request, 'An error occured when creating the team.');
            }

            // Insert drivers
            foreach ($data['drivers'] as $driver) {
                $row = [
                    'team_id' => $teamId,
                    'name' => $driver['name'],
                ];
                $driversStorage->insert($row);
            }

            $connection->commit();
        } catch (Exception $e) {
            $connection->rollBack();
            throw $e;
        }

        return $this->buildJsonResponse($request, $response);
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
        $teamName = $route->getArgument('team-name');

        /** @var \CkmTiming\Storages\v1\SantosEndurance\TeamsStorage $teamsStorage */
        $teamsStorage = $this->container->get('storages')['santos_endurance']['teams']();
        $teamsStorage->setTablesPrefix($tablesPrefix);
        $data = $teamsStorage->getByName($teamName);

        /** @var \CkmTiming\Storages\v1\SantosEndurance\DriversStorage $driversStorage */
        $driversStorage = $this->container->get('storages')['santos_endurance']['drivers']();
        $driversStorage->setTablesPrefix($tablesPrefix);
        $drivers = $driversStorage->getByTeamId($data['id']);
        $data['drivers'] = $drivers;

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
        $teamName = $route->getArgument('team-name');

        $data = $this->getParsedBody($request);
        $this->validatePutTeamValue($request, $data);

        /** @var \CkmTiming\Storages\v1\SantosEndurance\TeamsStorage $teamsStorage */
        $teamsStorage = $this->container->get('storages')['santos_endurance']['teams']();
        $teamsStorage->setTablesPrefix($tablesPrefix);
        $teamData = $teamsStorage->getByName($teamName);

        if (empty($teamData)) {
            throw new HttpBadRequestException($request, 'The team does not exists.');
        }

        // Update team
        $teamsStorage->update($teamData['id'], $data);

        return $this->buildJsonResponse($request, $response);
    }

    /**
     * @param Request $request
     * @param array $team
     * @return void
     */
    protected function validatePutTeamValue(Request $request, array $team) : void
    {
        /** @var \CkmTiming\Helpers\ValidatorTypes $validatorTypes */
        $validatorTypes = $this->container->get('validator_types')->setRequest($request);
        /** @var \CkmTiming\Helpers\ValidatorRanges $validatorRanges */
        $validatorRanges = $this->container->get('validator_ranges')->setRequest($request);

        // Values has correct format
        if (isset($team['name'])) {
            $validatorTypes->empty('name', $team['name'] ?? null);
            $validatorTypes->isString('name', $team['name']);
        }
        
        if (isset($team['number'])) {
            $validatorTypes->empty('number', $team['number'] ?? null);
            $validatorTypes->isInteger('number', $team['number']);
            $validatorRanges->isPositiveNumber('number', $team['number']);
        }
        
        if (isset($team['reference_time_offset'])) {
            $validatorTypes->isNull('reference_time_offset', $team['reference_time_offset'] ?? null);
            $validatorTypes->isInteger('reference_time_offset', $team['reference_time_offset']);
            $validatorRanges->isPositiveNumber('reference_time_offset', $team['reference_time_offset'], true);
        }
    }

    /**
     * @param Request $request
     * @param array $team
     * @return void
     */
    protected function validatePostTeamValueTypes(Request $request, array $team) : void
    {
        /** @var \CkmTiming\Helpers\ValidatorTypes $validatorTypes */
        $validatorTypes = $this->container->get('validator_types')->setRequest($request);

        // Values are set and not empty
        $validatorTypes->empty('name', $team['name'] ?? null);
        $validatorTypes->empty('number', $team['number'] ?? null);
        $validatorTypes->isNull('reference_time_offset', $team['reference_time_offset'] ?? null);
        $validatorTypes->isNull('drivers', $team['drivers'] ?? null);

        // Values has correct format
        $validatorTypes->isString('name', $team['name']);
        $validatorTypes->isInteger('number', $team['number']);
        $validatorTypes->isInteger('reference_time_offset', $team['reference_time_offset']);
        $validatorTypes->isArray('drivers', $team['drivers']);
    }

    /**
     * @param Request $request
     * @param array $team
     * @return void
     */
    protected function validatePostTeamValueRanges(Request $request, array $team) : void
    {
        /** @var \CkmTiming\Helpers\ValidatorRanges $validatorRanges */
        $validatorRanges = $this->container->get('validator_ranges')->setRequest($request);

        // Values has correct format
        $validatorRanges->isPositiveNumber('number', $team['number']);
        $validatorRanges->isPositiveNumber('reference_time_offset', $team['reference_time_offset'], true);
        $validatorRanges->itemsHasAttributes('drivers', $team['drivers'], $this->validDriverAttributes);
    }
}
