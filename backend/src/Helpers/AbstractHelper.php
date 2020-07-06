<?php
namespace CkmTiming\Helpers;

use Psr\Container\ContainerInterface as Container;
use Doctrine\DBAL\Connection;

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

    /**
     * @return Connection
     */
    protected function getConnection() : Connection
    {
        return $this->container->get('db');
    }
}
