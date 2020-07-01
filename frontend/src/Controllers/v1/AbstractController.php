<?php
namespace CkmTiming\Controllers\v1;

use Psr\Container\ContainerInterface;

abstract class AbstractController
{
    /** @var ContainerInterface */
    protected $container;

    /** @var \Slim\Views\Twig */
    protected $view;

    // constructor receives container instance
    public function __construct(ContainerInterface $c) {
        $this->container = $c;
        $this->view = $c->get('view');
    }
}
