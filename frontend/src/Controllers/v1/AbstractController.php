<?php
namespace CkmTiming\Controllers\v1;

use CkmTiming\Enumerations\Routes;
use Psr\Container\ContainerInterface;
use Psr\Http\Message\ServerRequestInterface as Request;

abstract class AbstractController
{
    /** @var ContainerInterface */
    protected $container;

    /** @var \Slim\Views\Twig */
    protected $view;

    /**
     * @param ContainerInterface $c
     */
    public function __construct(ContainerInterface $c)
    {
        $this->container = $c;
        $this->view = $c->get('view');
    }

    /**
     * Returns the basic params to use in the HTML view.
     * 
     * @param Request $request
     * @return array
     */
    protected function getViewParams(Request $request, $addPortRoute = true) : array
    {
        $uri = $request->getUri();
        $uri = [
            'scheme' => $uri->getScheme(),
            'host' => $uri->getHost(),
            'port' => $uri->getPort(),
            'path' => $uri->getPath(),
        ];

        $hostname = $uri['scheme'] . '://' . $uri['host'];
        $hostname .= $addPortRoute ? ':' . $uri['port'] : '';

        $routes = array_map(
            function ($route) use ($hostname) {
                return $hostname . $route;
            },
            Routes::getConstants()
        );
        foreach (Routes::getConstants() as $routeName => $routeValue) {
            $routes['_' . $routeName] = $routeValue;
        }

        $params = [
            'base_route' => $hostname,
            'routes' => $routes,
            'uri' => $uri,
            'env' => [
                'API_HOST' => getenv('API_HOST'),
                'API_PORT' => getenv('API_PORT'),
            ],
        ];
        return $params;
    }
}
