<?php
namespace CkmTiming\Middlewares;

use Psr\Container\ContainerInterface;

abstract class AbstractMiddleware
{
    /** @var ContainerInterface */
    protected $container;

    /**
     * @param ContainerInterface $container
     */
    public function __construct(ContainerInterface $container)
    {
        $this->container = $container;
    }
}
