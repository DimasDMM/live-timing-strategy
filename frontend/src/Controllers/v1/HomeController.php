<?php
namespace CkmTiming\Controllers\v1;

use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

class HomeController extends AbstractController
{
    public function get(Request $request, Response $response, array $args)
    {
        $html = $this->view->render($response, 'home.html', []);
        return $html;
    }
}
