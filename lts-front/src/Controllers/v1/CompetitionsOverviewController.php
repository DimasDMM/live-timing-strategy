<?php
namespace LTS\Controllers\v1;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

class CompetitionsOverviewController extends AbstractController
{
    /**
     * @param Request $request
     * @param Response $response
     * @param array $args Optional
     * @return Response
     */
    public function get(Request $request, Response $response, array $args = []) : Response
    {
        $competitionCode = $args['competition-code'];

        $viewParams = $this->getViewParams($request, $args);
        $viewParams['competition_code'] = $competitionCode;

        $html = $this->view->render(
            $response,
            'competitions_overview.html',
            $viewParams,
        );
        return $html;
    }
}
