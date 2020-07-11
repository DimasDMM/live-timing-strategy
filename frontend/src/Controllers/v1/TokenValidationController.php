<?php
namespace CkmTiming\Controllers\v1;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

class TokenValidationController extends AbstractController
{
    public function get(Request $request, Response $response, array $args)
    {
        $viewParams = $this->getViewParams($request);

        $html = $this->view->render($response, 'token_validation.html', $viewParams);
        return $html;
    }
}
