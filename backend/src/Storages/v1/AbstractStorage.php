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

    /**
     * @param array $row
     * @param string $table
     * @return void
     */
    protected function simpleInsert(array $row, string $table) : void
    {
        $queryBuilder = $this->getConnection()->createQueryBuilder();

        $rowValues = [];
        $rowParams = [];
        foreach ($row as $name => $value) {
            $paramName = ':' . $name;
            $rowParams[$paramName] = $value;
            $rowValues[$name] = $paramName;
        }

        $queryBuilder
            ->insert($table)
            ->values($rowValues)
            ->setParameters($rowParams);
        $queryBuilder->execute();
    }
}
