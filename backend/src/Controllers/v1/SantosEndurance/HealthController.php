<?php
namespace CkmTiming\Controllers\v1\SantosEndurance;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Exception\HttpBadRequestException;
use Slim\Routing\RouteContext;

class HealthController extends AbstractSantosEnduranceController
{
    protected $validHealthStatus = ['ok', 'warning', 'error', 'offline'];

    /**
     * @param Request $request
     * @param Response $response
     * @return Response
     */
    public function get(Request $request, Response $response) : Response
    {
        $eventIndex = $this->container->get('event-index');
        $tablesPrefix = $eventIndex['tables_prefix'];
        
        $eventStatsStorage = $this->container->get('storages')['santos_endurance']['health']();
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
        $healthCategory = $route->getArgument('health-category');
        $healthName = $route->getArgument('health-name');
        
        $healthStorage = $this->container->get('storages')['santos_endurance']['health']();
        $healthStorage->setTablesPrefix($tablesPrefix);
        $healthData = $healthStorage->getByName($healthCategory, $healthName);

        if (empty($healthData)) {
            throw new HttpBadRequestException($request, 'The health item does not exist.');
        }

        $data = $this->getParsedBody($request);
        $this->validatePutHealthValue($request, $data);

        $healthStorage->updateByName($healthCategory, $healthName, $data['status'], $data['message']);

        return $this->buildJsonResponse($request, $response);
    }

    /**
     * @param Request $request
     * @param array $data
     * @return void
     */
    protected function validatePutHealthValue(Request $request, array $data) : void
    {
        /** @var \CkmTiming\Helpers\ValidatorTypes $validatorTypes */
        $validatorTypes = $this->container->get('validator_types')->setRequest($request);

        /** @var \CkmTiming\Helpers\ValidatorRanges $validatorRanges */
        $validatorRanges = $this->container->get('validator_ranges')->setRequest($request);

        // Value is set
        $validatorTypes->empty('status', $data['status'] ?? null);
        $validatorTypes->isNull('message', $data['message'] ?? null);
        
        // Values has correct format
        $validatorRanges->inArray('status', $data['status'], $this->validHealthStatus);
        $validatorTypes->isString('message', $data['message']);
    }
}
