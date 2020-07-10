<?php
namespace CkmTiming\Controllers\v1\SantosEndurance;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Exception\HttpBadRequestException;
use Slim\Exception\HttpNotImplementedException;
use Slim\Routing\RouteContext;

class TimingController extends AbstractSantosEnduranceController
{
    protected $validStages = ['classification', 'race'];
    protected $validTimingTypes = ['onlap', 'real'];

    /**
     * @param Request $request
     * @param Response $response
     * @return Response
     */
    public function getAll(Request $request, Response $response) : Response
    {
        $eventIndex = $this->container->get('event-index');
        $tablesPrefix = $eventIndex['tables_prefix'];
        
        $routeContext = RouteContext::fromRequest($request);
        $route = $routeContext->getRoute();
        $timingType = $route->getArgument('timing-type');

        if (!in_array($timingType, $this->validTimingTypes)) {
            throw new HttpBadRequestException($request, 'Unknown timing type.');
        }

        /** @var \CkmTiming\Storages\v1\SantosEndurance\TimingStorage $timingStorage */
        $timingStorage = $this->container->get('storages')['santos_endurance']['timing']();
        $timingStorage->setTablesPrefix($tablesPrefix);
        $data = $timingStorage->getLastLap();

        // Cast integer and boolean values
        $data = $this->castTimingRows($data);

        if ($timingType == 'real') {
            // TO DO
            throw new HttpNotImplementedException($request);
            $data = $this->getRealTiming($data);
        }

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
    public function getByTeamName(Request $request, Response $response) : Response
    {
        $eventIndex = $this->container->get('event-index');
        $tablesPrefix = $eventIndex['tables_prefix'];
        
        $routeContext = RouteContext::fromRequest($request);
        $route = $routeContext->getRoute();
        $teamName = $route->getArgument('team-name');
        $limit = $route->getArgument('limit');

        if (!empty($limit)) {
            $this->validateLimit($request, $limit);
        }
        
        /** @var \CkmTiming\Storages\v1\SantosEndurance\TimingStorage $timingStorage */
        $timingStorage = $this->container->get('storages')['santos_endurance']['timing']();
        $timingStorage->setTablesPrefix($tablesPrefix);
        $data = $timingStorage->getByTeamName($teamName, $limit);

        // Cast integer and boolean values
        $data = $this->castTimingRows($data);

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
        $this->validatePostTimingValueTypes($request, $data);
        $this->validatePostTimingValueRanges($request, $data);

        /** @var \CkmTiming\Storages\v1\SantosEndurance\TimingStorage $timingStorage */
        $timingStorage = $this->container->get('storages')['santos_endurance']['timing']();
        $timingStorage->setTablesPrefix($tablesPrefix);

        // Get team and driver data
        /** @var \CkmTiming\Storages\v1\SantosEndurance\TeamsStorage $teamsStorage */
        $teamsStorage = $this->container->get('storages')['santos_endurance']['teams']();
        $teamsStorage->setTablesPrefix($tablesPrefix);
        $teamData = $teamsStorage->getByName($data['team_name']);
        if (empty($teamData)) {
            throw new HttpBadRequestException($request, 'The team does not exist.');
        }
        $teamId = $teamData['id'];

        if (!empty($data['driver_name'])) {
            /** @var \CkmTiming\Storages\v1\SantosEndurance\DriversStorage $driversStorage */
            $driversStorage = $this->container->get('storages')['santos_endurance']['drivers']();
            $driversStorage->setTablesPrefix($tablesPrefix);
            $driverData = $driversStorage->getByName($data['driver_name'], $teamId);
            if (empty($driverData)) {
                throw new HttpBadRequestException($request, 'The driver does not exist.');
            }
            $driverId = $driverData['id'];
        } else {
            $driverId = null;
        }

        // Get stage
        /** @var \CkmTiming\Storages\v1\SantosEndurance\StatsStorage $eventStatsStorage */
        $eventStatsStorage = $this->container->get('storages')['santos_endurance']['stats']();
        $eventStatsStorage->setTablesPrefix($tablesPrefix);
        $stage = $eventStatsStorage->getByName('stage')['value'];
        if (!in_array($stage, $this->validStages)) {
            throw new HttpBadRequestException($request, 'Cannot insert the time due to the stage is unknown.');
        }

        // Get last known kart status
        $lastKnown = $timingStorage->getLastKnownKartStatus($teamId, (int)$data['number_stops']);
        if (empty($lastKnown)) {
            $kartStatus = 'unknown';
            $kartStatusGuess = null;
            $forcedKartStatus = null;
        } else {
            $kartStatus = $lastKnown['kart_status'];
            $kartStatusGuess = $lastKnown['kart_status_guess'];
            $forcedKartStatus = $lastKnown['forced_kart_status'];
        }

        // Insert time
        $row = [
            'team_id' => $teamId,
            'driver_id' => $driverId,
            'position' => (int)$data['position'],
            'time' => (int)$data['time'],
            'lap' => (int)$data['lap'],
            'gap' => (int)$data['gap'],
            'stage' => $stage,
            'kart_status' => $kartStatus,
            'kart_status_guess' => $kartStatusGuess,
            'forced_kart_status' => $forcedKartStatus,
        ];
        $timingStorage->insert($row);

        return $this->buildJsonResponse($request, $response);
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

    /**
     * @param Request $request
     * @param array $data
     * @return void
     */
    protected function validatePostTimingValueTypes(Request $request, array $data) : void
    {
        /** @var \CkmTiming\Helpers\ValidatorTypes $validatorTypes */
        $validatorTypes = $this->container->get('validator_types')->setRequest($request);

        // Values are set and not empty
        $validatorTypes->empty('position', $data['position'] ?? null);
        $validatorTypes->empty('team_name', $data['team_name'] ?? null);
        $validatorTypes->empty('time', $data['time'] ?? null);
        $validatorTypes->empty('gap', $data['gap'] ?? null);
        $validatorTypes->empty('lap', $data['lap'] ?? null);
        $validatorTypes->isNull('number_stops', $data['number_stops'] ?? null);

        // Values has correct format
        if (!empty($data['driver_name'])) {
            $validatorTypes->isString('driver_name', $data['driver_name']);
        }
        $validatorTypes->isInteger('position', $data['position']);
        $validatorTypes->isString('team_name', $data['team_name']);
        $validatorTypes->isInteger('time', $data['time']);
        $validatorTypes->isInteger('gap', $data['gap']);
        $validatorTypes->isInteger('lap', $data['lap']);
        $validatorTypes->isInteger('number_stops', $data['number_stops']);
    }

    /**
     * @param Request $request
     * @param array $data
     * @return void
     */
    protected function validatePostTimingValueRanges(Request $request, array $data) : void
    {
        /** @var \CkmTiming\Helpers\ValidatorRanges $validatorRanges */
        $validatorRanges = $this->container->get('validator_ranges')->setRequest($request);

        // Values has correct format
        $validatorRanges->isPositiveNumber('position', $data['position']);
        $validatorRanges->isPositiveNumber('time', $data['time']);
        $validatorRanges->isPositiveNumber('gap', $data['gap'], true);
        $validatorRanges->isPositiveNumber('lap', $data['lap']);
        $validatorRanges->isPositiveNumber('number_stops', $data['number_stops'], true);
    }

    protected function getRealTiming(array $data) : array
    {
        $eventIndex = $this->container->get('event-index');
        $tablesPrefix = $eventIndex['tables_prefix'];
        
        /** @var \CkmTiming\Storages\v1\SantosEndurance\ConfigurationStorage $configurationStorage */
        $configurationStorage = $this->container->get('storages')['santos_endurance']['configuration']();
        $configurationStorage->setTablesPrefix($tablesPrefix);
        $configDataNoIndex = $configurationStorage->getAll();
        $configData = [];
        foreach ($configDataNoIndex as $row) {
            $configData[$row['name']] = $row['value'];
        }
        
        /** @var \CkmTiming\Storages\v1\SantosEndurance\StatsStorage $statsStorage */
        $eventStatsStorage = $this->container->get('storages')['santos_endurance']['stats']();
        $eventStatsStorage->setTablesPrefix($tablesPrefix);
        $statsDataNoIndex = $eventStatsStorage->getAll();
        $statsData = [];
        foreach ($statsDataNoIndex as $row) {
            $statsData[$row['name']] = $row['value'];
        }

        $lapTime = $statsData['reference_time'] + $statsData['reference_current_offset'];

        return array_map(
            function ($row) use ($configData) {
                return [
                    'team_name' => $row['team_name'],
                    'team_number' => $row['team_number'],
                    'team_reference_time_offset' => $row['team_reference_time_offset'],
                    'driver_name' => $row['driver_name'],
                    'driver_reference_time_offset' => $row['driver_reference_time_offset'],
                    'driver_time_driving' => $row['driver_time_driving'],
                    'position' => $row['position'],
                    'time' => $row['time'],
                    'lap' => $row['lap'],
                    'gap' => $row['gap'],
                    'stage' => $row['stage'],
                    'kart_status' => $row['kart_status'],
                    'kart_status_guess' => $row['kart_status_guess'],
                    'forced_kart_status' => $row['forced_kart_status'],
                    'number_stops' => $row['number_stops'],
                    'is_stop' => $row['is_stop'],
                ];
            },
            $data
        );
    }

    /**
     * @param array $data
     * @return array
     */
    protected function castTimingRows(array $data) : array
    {
        return array_map(
            function ($row) {
                return [
                    'team_name' => $row['team_name'],
                    'team_number' => (int)$row['team_number'],
                    'team_reference_time_offset' => (int)$row['team_reference_time_offset'],
                    'driver_name' => $row['driver_name'],
                    'driver_reference_time_offset' => isset($row['driver_reference_time_offset']) ? (int)$row['driver_reference_time_offset'] : null,
                    'driver_time_driving' =>  isset($row['driver_time_driving']) ? (int)$row['driver_time_driving'] : null,
                    'position' => (int)$row['position'],
                    'time' => (int)$row['time'],
                    'lap' => (int)$row['lap'],
                    'gap' => (int)$row['gap'],
                    'stage' => $row['stage'],
                    'kart_status' => $row['kart_status'],
                    'kart_status_guess' => $row['kart_status_guess'],
                    'forced_kart_status' => $row['forced_kart_status'],
                    'number_stops' => (int)$row['number_stops'],
                    'is_stop' => (bool)$row['is_stop'],
                ];
            },
            $data
        );
    }
}
