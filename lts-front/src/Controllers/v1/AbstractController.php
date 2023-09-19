<?php
namespace LTS\Controllers\v1;

use LTS\Enumerations\Routes;
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
     * @param array $args Optional
     * @param bool $addPortRoute Optional
     * @return array
     */
    protected function getViewParams(Request $request, $args = [], $addPortRoute = true) : array
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

        $routes = $this->replacePlaceholders($routes, $args);

        $params = [
            'base_route' => $hostname,
            'routes' => $routes,
            'uri' => $uri,
            'env' => [
                'API_HOST' => getenv('API_HOST'),
                'API_PORT' => getenv('API_PORT'),
                'API_VERSION' => getenv('API_VERSION'),
            ],
        ];
        return $params;
    }

    /**
     * @param array $routes
     * @param array $args
     * @return array
     */
    protected function replacePlaceholders(array $routes, array $args) : array
    {
        if (empty($args)) {
            return $routes;
        }

        return array_map(
            function ($route) use ($args) {
                foreach ($args as $varName => $varValue) {
                    $route = preg_replace('/\{' . $varName . '\}/', $varValue, $route);
                }
                return $route;
            },
            $routes
        );
    }
}
