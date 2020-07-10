<?php
namespace CkmTiming\Controllers\v1\SantosEndurance;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Exception\HttpBadRequestException;
use Slim\Routing\RouteContext;

class ConfigurationController extends AbstractSantosEnduranceController
{
    protected $validLengthUnits = ['laps', 'hours'];

    /**
     * @param Request $request
     * @param Response $response
     * @return Response
     */
    public function get(Request $request, Response $response) : Response
    {
        $eventIndex = $this->container->get('event-index');
        $tablesPrefix = $eventIndex['tables_prefix'];
        
        $eventStatsStorage = $this->container->get('storages')['santos_endurance']['configuration']();
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
