<?php
namespace CkmTiming\Controllers\v1;

use CkmTiming\Enumerations\Roles;
use Exception;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Exception\HttpBadRequestException;

class EventController extends AbstractController
{
    protected $validTrackNames = ['santos'];
    protected $validEventTypes = ['endurance'];
    protected $validRaceLengthUnits = ['laps', 'hours'];

    /**
     * @param Request $request
     * @param Response $response
     * @return Response
     */
    public function get(Request $request, Response $response) : Response
    {
        $eventsIndexStorage = $this->container->get('storages')['common']['events_index']();
        $data = $eventsIndexStorage->getAll();

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
        $this->validateRole($request, [Roles::ADMIN, Roles::BATCH]);
        $eventsIndexStorage = $this->container->get('storages')['common']['events_index']();

        $data = $this->getParsedBody($request);
        $this->validateEventValueTypes($request, $data);
        $this->validateEventValueRanges($request, $data);
        
        $event = $eventsIndexStorage->getByName($data['name']);
        if (!empty($event)) {
            throw new HttpBadRequestException($request, 'Event name already exists.');
        }

        // Start transaction
        $connection = $this->getConnection();
        $connection->beginTransaction();
        try {
            $eventCreator = $this->container->get('event_creator');
            if (!$eventCreator->isEventSupported($data['track_name'], $data['event_type'])) {
                throw new HttpBadRequestException($request, 'The event type is not supported in this track.');
            }

            $tablesPrefix = $eventCreator->getTablesPrefix($data['name']);
            $eventCreator->createEventTables($data['track_name'], $data['event_type'], $tablesPrefix);

            $event = [
                'name' => $data['name'],
                'tables_prefix' => $tablesPrefix,
                'track_name' => $data['track_name'],
                'event_type' => $data['event_type'],
            ];
            $eventsIndexStorage->insert($event);
            
            // Set config items
            $eventConfigStorage = $this->container->get('storages')['santos_endurance']['configuration']();
            $eventConfigStorage->setTablesPrefix($tablesPrefix);
            $eventConfigStorage->updateByName($eventConfigStorage::RACE_LENGTH, (string)$data['configuration']['race_length']);
            $eventConfigStorage->updateByName($eventConfigStorage::RACE_LENGTH_UNIT, (string)$data['configuration']['race_length_unit']);
            $eventConfigStorage->updateByName($eventConfigStorage::REFERENCE_TIME_TOP_TEAMS, (string)$data['configuration']['reference_time_top_teams']);

            $connection->commit();
        } catch (Exception $e) {
            $connection->rollBack();
            throw $e;
        }

        return $this->buildJsonResponse($request, $response);
    }

    /**
     * @param Request $request
     * @param array $event
     * @return void
     */
    protected function validateEventValueTypes(Request $request, array $event) : void
    {
        /** @var \CkmTiming\Helpers\ValidatorTypes $validatorTypes */
        $validatorTypes = $this->container->get('validator_types')->setRequest($request);

        // Values are set and not empty
        $validatorTypes->empty('name', $event['name'] ?? null);
        $validatorTypes->empty('track_name', $event['track_name'] ?? null);
        $validatorTypes->empty('event_type', $event['event_type'] ?? null);
        $validatorTypes->empty('configuration', $event['configuration'] ?? null);
        
        $validatorTypes->empty('configuration->race_length', $event['configuration']['race_length'] ?? null);
        $validatorTypes->empty('configuration->race_length_unit', $event['configuration']['race_length_unit'] ?? null);
        $validatorTypes->empty('configuration->reference_time_top_teams', $event['configuration']['reference_time_top_teams'] ?? null);

        // Values has correct format
        $validatorTypes->isArray('configuration', $event['configuration']);
        $validatorTypes->isString('name', $event['name']);
        $validatorTypes->isString('track_name', $event['track_name']);
        $validatorTypes->isString('event_type', $event['event_type']);
        $validatorTypes->isInteger('configuration->race_length', $event['configuration']['race_length']);
        $validatorTypes->isString('configuration->race_length_unit', $event['configuration']['race_length_unit']);
        $validatorTypes->isInteger('configuration->reference_time_top_teams', $event['configuration']['reference_time_top_teams']);
    }

    /**
     * @param Request $request
     * @param array $event
     * @return void
     */
    protected function validateEventValueRanges(Request $request, array $event) : void
    {
        /** @var \CkmTiming\Helpers\ValidatorRanges $validatorRanges */
        $validatorRanges = $this->container->get('validator_ranges')->setRequest($request);

        // Values has correct format
        $validatorRanges->inArray('track_name', $event['track_name'], $this->validTrackNames);
        $validatorRanges->inArray('event_type', $event['event_type'], $this->validEventTypes);
        $validatorRanges->isPositiveNumber('configuration->race_length', $event['configuration']['race_length']);
        $validatorRanges->inArray('configuration->race_length_unit', $event['configuration']['race_length_unit'], $this->validRaceLengthUnits);
        $validatorRanges->isPositiveNumber('configuration->reference_time_top_teams', $event['configuration']['reference_time_top_teams']);
    }
}
