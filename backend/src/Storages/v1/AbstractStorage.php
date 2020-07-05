<?php
namespace CkmTiming\Storages\v1;

use Doctrine\DBAL\Connection;
use Psr\Container\ContainerInterface as Container;

abstract class AbstractStorage
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
