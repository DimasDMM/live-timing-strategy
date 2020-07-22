<?php
namespace CkmTiming\Controllers\v1\SantosEndurance;

use Exception;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Exception\HttpBadRequestException;
use Slim\Exception\HttpNotFoundException;
use Slim\Routing\RouteContext;

class KartsBoxController extends AbstractSantosEnduranceController
{
    protected $validKartStatus = ['unknown', 'good', 'medium', 'bad'];

    /**
     * @param Request $request
     * @param Response $response
     * @return Response
     */
    public function get(Request $request, Response $response) : Response
    {
        $routeContext = RouteContext::fromRequest($request);
        $route = $routeContext->getRoute();
        $kartAction = $route->getArgument('kart-action');

        if ($kartAction == 'probs') {
            return $this->getProbs($request, $response);
        } elseif ($kartAction == 'in' || $kartAction == 'out') {
            return $this->getInOut($request, $response, $kartAction);
        }

        throw new HttpNotFoundException($request);
    }

    /**
     * @param Request $request
     * @param Response $response
     * @return Response
     */
    protected function getProbs(Request $request, Response $response) : Response
    {
        $eventIndex = $this->container->get('event-index');
        $tablesPrefix = $eventIndex['tables_prefix'];
        
        /** @var \CkmTiming\Storages\v1\SantosEndurance\KartsBoxProbsStorage $kartsProbsStorage */
        $kartsProbsStorage = $this->container->get('storages')['santos_endurance']['karts-box-probs']();
        $kartsProbsStorage->setTablesPrefix($tablesPrefix);
        $data = $kartsProbsStorage->getAll();

        return $this->buildJsonResponse(
            $request,
            $response,
            $data
        );
    }

    /**
     * @param Request $request
     * @param Response $response
     * @param string $kartAction
     * @return Response
     */
    protected function getInOut(Request $request, Response $response, string $kartAction) : Response
    {
        $eventIndex = $this->container->get('event-index');
        $tablesPrefix = $eventIndex['tables_prefix'];
        
        /** @var \CkmTiming\Storages\v1\SantosEndurance\KartsBoxInStorage $kartsProbsStorage */
        $storageKey = $kartAction == 'in' ? 'karts-box-in' : 'karts-box-out';
        $kartsInOutStorage = $this->container->get('storages')['santos_endurance'][$storageKey]();
        $kartsInOutStorage->setTablesPrefix($tablesPrefix);
        $data = $kartsInOutStorage->getAll();

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
        $routeContext = RouteContext::fromRequest($request);
        $route = $routeContext->getRoute();
        $kartAction = $route->getArgument('kart-action');

        if ($kartAction == 'probs') {
            return $this->postProbs($request, $response);
        } elseif ($kartAction == 'in' || $kartAction == 'out') {
            return $this->postInOut($request, $response, $kartAction);
        }

        throw new HttpNotFoundException($request);
    }

    /**
     * @param Request $request
     * @param Response $response
     * @return Response
     * @throws HttpBadRequestException
     */
    protected function postProbs(Request $request, Response $response) : Response
    {
        $eventIndex = $this->container->get('event-index');
        $tablesPrefix = $eventIndex['tables_prefix'];

        $data = $this->getParsedBody($request);
        $this->validateProbsValueTypes($request, $data);
        $this->validateProbsValueRanges($request, $data);

        /** @var \CkmTiming\Storages\v1\SantosEndurance\KartsBoxProbsStorage $kartsProbsStorage */
        $kartsProbsStorage = $this->container->get('storages')['santos_endurance']['karts-box-probs']();
        $kartsProbsStorage->setTablesPrefix($tablesPrefix);
        $kartsProbsStorage->insert($data);

        return $this->buildJsonResponse($request, $response);
    }

    /**
     * @param Request $request
     * @param Response $response
     * @param string $kartAction
     * @return Response
     * @throws HttpBadRequestException
     */
    protected function postInOut(Request $request, Response $response, string $kartAction) : Response
    {
        $eventIndex = $this->container->get('event-index');
        $tablesPrefix = $eventIndex['tables_prefix'];

        $data = $this->getParsedBody($request);
        $this->validateInOutValueTypes($request, $data);

        /** @var \CkmTiming\Storages\v1\SantosEndurance\TeamsStorage $teamsStorage */
        $teamsStorage = $this->container->get('storages')['santos_endurance']['teams']();
        $teamsStorage->setTablesPrefix($tablesPrefix);
        $teamData = $teamsStorage->getByName($data['team_name']);

        if (empty($teamData)) {
            throw new HttpBadRequestException($request, 'The team does not exist.');
        }

        $teamId = $teamData['id'];

        if (empty($data['kart_status'])) {
            // Inherit kart status from last lap time
            /** @var \CkmTiming\Storages\v1\SantosEndurance\TimingStorage $timingStorage */
            $timingStorage = $this->container->get('storages')['santos_endurance']['timing']();
            $timingStorage->setTablesPrefix($tablesPrefix);

            $lastKnown = $timingStorage->getLastKnownKartStatus($teamId);
            $kartStatus = isset($lastKnown['kart_status']) ? $lastKnown['kart_status'] : 'unknown';
            $forcedKartStatus = isset($lastKnown['forced_kart_status']) ? $lastKnown['forced_kart_status'] : null;
        } else {
            $kartStatus = $data['kart_status'];
            $forcedKartStatus = $data['forced_kart_status'];
        }

        $kartInOutData = [
            'kart_status' => $kartStatus,
            'forced_kart_status' => $forcedKartStatus,
            'team_id' => $teamId,
        ];

        /** @var \CkmTiming\Storages\v1\SantosEndurance\KartsBoxInStorage $kartsInOutStorage */
        $storageKey = $kartAction == 'in' ? 'karts-box-in' : 'karts-box-out';
        $kartsInOutStorage = $this->container->get('storages')['santos_endurance'][$storageKey]();
        $kartsInOutStorage->setTablesPrefix($tablesPrefix);
        $kartsInOutStorage->insert($kartInOutData);

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

        $data = $this->getParsedBody($request);
        $this->validateProbsValueTypes($request, $data);
        $this->validateProbsValueRanges($request, $data);

        /** @var \CkmTiming\Storages\v1\SantosEndurance\KartsBoxProbsStorage $kartsProbsStorage */
        $kartsProbsStorage = $this->container->get('storages')['santos_endurance']['karts-box-probs']();
        $kartsProbsStorage->setTablesPrefix($tablesPrefix);

        $kartsProbsStorage->updateByStep($data['step'], $data['kart_status'], $data['probability']);

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
        $validatorTypes->isNull('reference_time_offset', $team['reference_time_offset'] ?? null);
        $validatorRanges->isPositiveNumber('reference_time_offset', $team['reference_time_offset'], true);
    }

    /**
     * @param Request $request
     * @param array $prob
     * @return void
     */
    protected function validateProbsValueTypes(Request $request, array $prob) : void
    {
        /** @var \CkmTiming\Helpers\ValidatorTypes $validatorTypes */
        $validatorTypes = $this->container->get('validator_types')->setRequest($request);

        // Values are set and not empty
        $validatorTypes->isNull('step', $prob['step'] ?? null);
        $validatorTypes->empty('kart_status', $prob['kart_status'] ?? null);
        $validatorTypes->empty('probability', $prob['probability'] ?? null);

        // Values has correct format
        $validatorTypes->isInteger('step', $prob['step']);
        $validatorTypes->isString('kart_status', $prob['kart_status']);
        $validatorTypes->isNumeric('probability', $prob['probability']);
    }

    /**
     * @param Request $request
     * @param array $prob
     * @return void
     */
    protected function validateProbsValueRanges(Request $request, array $prob) : void
    {
        /** @var \CkmTiming\Helpers\ValidatorRanges $validatorRanges */
        $validatorRanges = $this->container->get('validator_ranges')->setRequest($request);

        // Values has correct format
        $validatorRanges->isPositiveNumber('step', $prob['step'], true);
        $validatorRanges->inArray('kart_status', $prob['kart_status'], $this->validKartStatus);
        $validatorRanges->isPositiveNumber('probability', $prob['probability'], true);
    }

    /**
     * @param Request $request
     * @param array $kartInOut
     * @return void
     */
    protected function validateInOutValueTypes(Request $request, array $kartInOut) : void
    {
        /** @var \CkmTiming\Helpers\ValidatorTypes $validatorTypes */
        $validatorTypes = $this->container->get('validator_types')->setRequest($request);

        // Values are set and not empty
        $validatorTypes->empty('team_name', $kartInOut['team_name'] ?? null);
        $validatorTypes->empty('kart_status', $kartInOut['kart_status'] ?? null);

        // Values has correct format
        $validatorTypes->isString('team_name', $kartInOut['team_name']);
        if (!empty($kartInOut['kart_status'])) {
            $validatorTypes->isString('kart_status', $kartInOut['kart_status']);
        }
        if (!empty($kartInOut['forced_kart_status'])) {
            $validatorTypes->isString('forced_kart_status', $kartInOut['forced_kart_status']);
        }
    }
}
