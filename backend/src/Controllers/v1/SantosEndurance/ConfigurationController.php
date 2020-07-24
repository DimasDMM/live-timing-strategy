<?php
namespace CkmTiming\Controllers\v1\SantosEndurance;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Exception\HttpBadRequestException;
use Slim\Routing\RouteContext;

class ConfigurationController extends AbstractSantosEnduranceController
{
    protected $validLengthUnits = ['laps', 'milli'];

    /**
     * @param Request $request
     * @param Response $response
     * @return Response
     */
    public function get(Request $request, Response $response) : Response
    {
        $eventIndex = $this->container->get('event-index');
        $tablesPrefix = $eventIndex['tables_prefix'];
        
        /** @var \CkmTiming\Storages\v1\SantosEndurance\ConfigurationStorage $configurationStorage */
        $configurationStorage = $this->container->get('storages')['santos_endurance']['configuration']();
        $configurationStorage->setTablesPrefix($tablesPrefix);
        $data = $configurationStorage->getAll();

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
    public function put(Request $request, Response $response) : Response
    {
        $eventIndex = $this->container->get('event-index');
        $tablesPrefix = $eventIndex['tables_prefix'];

        $data = $this->getParsedBody($request);
        $this->validatePutConfigValues($request, $data);

        /** @var \CkmTiming\Storages\v1\SantosEndurance\ConfigurationStorage $configurationStorage */
        $configurationStorage = $this->container->get('storages')['santos_endurance']['configuration']();
        $configurationStorage->setTablesPrefix($tablesPrefix);

        foreach ($data as $configName => $configValue) {
            $configurationStorage->updateByName($configName, $configValue);
        }

        return $this->buildJsonResponse($request, $response);
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
        $configName = $route->getArgument('config-name');
        
        /** @var \CkmTiming\Storages\v1\SantosEndurance\ConfigurationStorage $configurationStorage */
        $configurationStorage = $this->container->get('storages')['santos_endurance']['configuration']();
        $configurationStorage->setTablesPrefix($tablesPrefix);
        $configData = $configurationStorage->getByName($configName);

        if (empty($configData)) {
            throw new HttpBadRequestException($request, 'The configuration item does not exist.');
        }

        $data = $this->getParsedBody($request);
        $this->validatePutConfigValue($request, $data, $configName);

        $configurationStorage->updateByName($configName, $data['value']);

        return $this->buildJsonResponse($request, $response);
    }

    /**
     * @param Request $request
     * @param array $data
     * @return void
     */
    protected function validatePutConfigValues(Request $request, array $data) : void
    {
        /** @var \CkmTiming\Helpers\ValidatorTypes $validatorTypes */
        $validatorTypes = $this->container->get('validator_types')->setRequest($request);
        /** @var \CkmTiming\Helpers\ValidatorRanges $validatorRanges */
        $validatorRanges = $this->container->get('validator_ranges')->setRequest($request);

        // Values are set
        $validatorTypes->empty('race_length', $data['race_length'] ?? null);
        $validatorTypes->empty('race_length_unit', $data['race_length_unit'] ?? null);
        $validatorTypes->empty('reference_time_top_teams', $data['reference_time_top_teams'] ?? null);
        $validatorTypes->empty('karts_in_box', $data['karts_in_box'] ?? null);
        $validatorTypes->empty('stop_time', $data['stop_time'] ?? null);
        $validatorTypes->empty('min_number_stops', $data['min_number_stops'] ?? null);
        
        // Values has correct format
        $validatorTypes->isNumeric('race_length', $data['race_length']);
        $validatorRanges->isPositiveNumber('race_length', (int)$data['race_length']);
        $validatorRanges->inArray('race_length_unit', $data['race_length_unit'], $this->validLengthUnits);
        
        $validatorTypes->isNumeric('reference_time_top_teams', $data['reference_time_top_teams']);
        $validatorRanges->isPositiveNumber('reference_time_top_teams', (int)$data['reference_time_top_teams']);
        
        $validatorTypes->isNumeric('karts_in_box', $data['karts_in_box']);
        $validatorRanges->isPositiveNumber('karts_in_box', (int)$data['karts_in_box']);
        
        $validatorTypes->isNumeric('stop_time', $data['stop_time']);
        $validatorRanges->isPositiveNumber('stop_time', (int)$data['stop_time']);

        $validatorTypes->isNumeric('min_number_stops', $data['min_number_stops']);
        $validatorRanges->isPositiveNumber('min_number_stops', (int)$data['min_number_stops']);
    }

    /**
     * @param Request $request
     * @param array $configData
     * @param string $configName
     * @return void
     */
    protected function validatePutConfigValue(Request $request, array $configData, string $configName) : void
    {
        /** @var \CkmTiming\Helpers\ValidatorTypes $validatorTypes */
        $validatorTypes = $this->container->get('validator_types')->setRequest($request);
        /** @var \CkmTiming\Helpers\ValidatorRanges $validatorRanges */
        $validatorRanges = $this->container->get('validator_ranges')->setRequest($request);

        // Value is set
        $validatorTypes->isNull('value', $configData['value'] ?? null);
        
        // Values has correct format
        switch ($configName) {
            case 'stop_time':
                $validatorTypes->isNumeric('stop_time', $configData['value']);
                $validatorRanges->isPositiveNumber('stop_time', (int)$configData['value']);
                break;
            case 'min_number_stops':
                $validatorTypes->isNumeric('min_number_stops', $configData['value']);
                $validatorRanges->isPositiveNumber('min_number_stops', (int)$configData['value']);
                break;
            case 'karts_in_box':
                $validatorTypes->isNumeric('karts_in_box', $configData['value']);
                $validatorRanges->isPositiveNumber('karts_in_box', (int)$configData['value']);
                break;
            case 'race_length':
                $validatorTypes->isNumeric('race_length', $configData['value']);
                $validatorRanges->isPositiveNumber('race_length', (int)$configData['value']);
                break;
            case 'race_length_unit':
                $validatorTypes->isString('race_length_unit', $configData['value']);
                $validatorRanges->inArray('race_length_unit', $configData['value'], $this->validLengthUnits);
                break;
            case 'reference_time_top_teams':
                $validatorTypes->isNumeric('reference_time_top_teams', $configData['value']);
                $validatorRanges->isPositiveNumber('reference_time_top_teams', (int)$configData['value']);
                break;
        }
    }
}
