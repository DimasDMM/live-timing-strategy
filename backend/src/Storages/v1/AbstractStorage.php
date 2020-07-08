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
     * @param array $data
     * @param string $table
     * @return void
     */
    protected function simpleInsert(array $data, string $table) : void
    {
        $queryBuilder = $this->getConnection()->createQueryBuilder();

        $rowValues = [];
        $rowParams = [];
        foreach ($data as $column => $value) {
            $paramName = ':' . $column;
            $rowParams[$paramName] = $value;
            $rowValues[$column] = $paramName;
        }

        $queryBuilder
            ->insert($table)
            ->values($rowValues)
            ->setParameters($rowParams);
        $queryBuilder->execute();
    }

    /**
     * @param array $data
     * @param string $table
     * @param string|int $id
     * @param string $colId
     * @return void
     */
    protected function simpleUpdate(array $data, string $table, $id, string $colId = 'id') : void
    {
        $queryBuilder = $this->getConnection()->createQueryBuilder();
        $queryBuilder->update($table, 'u');

        foreach ($data as $column => $value) {
            $paramName = ':' . $column;
            $queryBuilder
                ->set("u.$column", $paramName)
                ->setParameter($column, $value);
        }

        $queryBuilder->where($queryBuilder->expr()->eq("u.$colId", ':id_column'));
        $queryBuilder->setParameter(':id_column', $id);

        $queryBuilder->execute();
    }
}
