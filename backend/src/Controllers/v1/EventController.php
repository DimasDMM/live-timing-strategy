<?php
namespace CkmTiming\Controllers\v1;

use CkmTiming\Enumerations\Roles;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

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
     */
    public function post(Request $request, Response $response) : Response
    {
        $this->validateRole($request, [Roles::ADMIN, Roles::BATCH]);
        $eventsIndexStorage = $this->container->get('storages')['common']['events_index']();

        $content = $this->getParsedBody($request);
        var_dump($content);

        $this->validateEventValueTypes($request, $content);
        $this->validateEventValueRanges($request, $content);
        die();

        $data = $this->container->get('logged');
        return $this->buildJsonResponse(
            $request,
            $response,
            $data
        );
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
        $validatorTypes->empty('track_name', $event['track_name'] ?? null);
        $validatorTypes->empty('race_type', $event['race_type'] ?? null);
        $validatorTypes->empty('race_length', $event['race_length'] ?? null);
        $validatorTypes->empty('race_length_unit', $event['race_length_unit'] ?? null);
        $validatorTypes->empty('reference_time_top_teams', $event['reference_time_top_teams'] ?? null);

        // Values has correct format
        $validatorTypes->isString('track_name', $event['track_name']);
        $validatorTypes->isString('race_type', $event['race_type']);
        $validatorTypes->isInteger('race_length', $event['race_length']);
        $validatorTypes->isString('race_length_unit', $event['race_length_unit']);
        $validatorTypes->isInteger('reference_time_top_teams', $event['reference_time_top_teams']);
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
        $validatorRanges->isValidRaceType('race_type', $event['race_type']);
        $validatorRanges->isPositiveNumber('race_length', $event['race_length']);
        $validatorRanges->isValidRaceLengthUnit('race_length_unit', $event['race_length_unit']);
        $validatorRanges->isPositiveNumber('reference_time_top_teams', $event['reference_time_top_teams']);
    }
}
