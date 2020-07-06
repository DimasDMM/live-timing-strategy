<?php
namespace CkmTiming\Controllers\v1;

use CkmTiming\Enumerations\Roles;
use Exception;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Exception\HttpBadRequestException;

class EventController extends AbstractController
{
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

        $content = $this->getParsedBody($request);

        $this->validateEventValueTypes($request, $content);
        $this->validateEventValueRanges($request, $content);
        
        $event = $eventsIndexStorage->getByName($content['event_name']);
        if (!empty($event)) {
            throw new HttpBadRequestException($request, 'Event name already exists.');
        }

        // Start transaction
        $connection = $this->getConnection();
        $connection->beginTransaction();
        try {
            $eventCreator = $this->container->get('event_creator');
            if (!$eventCreator->isEventSupported($content['track_name'], $content['event_type'])) {
                throw new HttpBadRequestException($request, 'The event type is not supported in this track.');
            }

            $tablesPrefix = $eventCreator->getTablesPrefix($content['event_name']);
            $eventCreator->createEventTables($content['track_name'], $content['event_type'], $tablesPrefix);

            $eventsIndexStorage->insert($content['event_name'], $tablesPrefix, $content['track_name'], $content['event_type']);
            
            // Set config items
            $eventConfigStorage = $this->container->get('storages')['santos_endurance']['event_config']();
            $eventConfigStorage->setTablesPrefix($tablesPrefix);
            $eventConfigStorage->updateByName($eventConfigStorage::RACE_LENGTH, (string)$content['configuration']['race_length']);
            $eventConfigStorage->updateByName($eventConfigStorage::RACE_LENGTH_UNIT, (string)$content['configuration']['race_length_unit']);
            $eventConfigStorage->updateByName($eventConfigStorage::REFERENCE_TIME_TOP_TEAMS, (string)$content['configuration']['reference_time_top_teams']);

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
        $validatorTypes = $this->container->get('validator_types')->setRequest($request);

        // Values are set and not empty
        $validatorTypes->empty('event_name', $event['event_name'] ?? null);
        $validatorTypes->empty('track_name', $event['track_name'] ?? null);
        $validatorTypes->empty('event_type', $event['event_type'] ?? null);
        $validatorTypes->empty('configuration', $event['configuration'] ?? null);
        
        $validatorTypes->empty('configuration->race_length', $event['configuration']['race_length'] ?? null);
        $validatorTypes->empty('configuration->race_length_unit', $event['configuration']['race_length_unit'] ?? null);
        $validatorTypes->empty('configuration->reference_time_top_teams', $event['configuration']['reference_time_top_teams'] ?? null);

        // Values has correct format
        $validatorTypes->isString('configuration', $event['configuration']);
        $validatorTypes->isString('event_name', $event['event_name']);
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
        $validatorRanges = $this->container->get('validator_ranges')->setRequest($request);

        // Values has correct format
        $validatorRanges->isValidTrackName('track_name', $event['track_name']);
        $validatorRanges->isValidRaceType('event_type', $event['event_type']);
        $validatorRanges->isPositiveNumber('configuration->race_length', $event['configuration']['race_length']);
        $validatorRanges->isValidRaceLengthUnit('configuration->race_length_unit', $event['configuration']['race_length_unit']);
        $validatorRanges->isPositiveNumber('configuration->reference_time_top_teams', $event['configuration']['reference_time_top_teams']);
    }
}
