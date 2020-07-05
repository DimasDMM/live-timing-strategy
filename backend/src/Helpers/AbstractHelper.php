<?php
namespace CkmTiming\Helpers;

use Psr\Container\ContainerInterface as Container;

abstract class AbstractHelper
{
    /** @var Container */
    protected $container;

    /**
     * @param Container $container
     */
    public function __construct(Container $container)
    {
        $this->container = $container;
    }
}
