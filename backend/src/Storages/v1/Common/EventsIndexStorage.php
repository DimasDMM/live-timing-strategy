<?php
namespace CkmTiming\Storages\v1\Common;

use CkmTiming\Enumerations\Tables;
use CkmTiming\Storages\v1\AbstractStorage;

class EventsIndexStorage extends AbstractStorage
{
    /**
     * @return array
     */
    public function getAll() : array
    {
        $connection = $this->getConnection();
        $stmt = "
            SELECT
                ei.id,
                ei.name,
                ei.tables_prefix,
                ei.track_name,
                ei.event_type,
                ei.update_date
            FROM " . Tables::EVENTS_INDEX . " ei
            ORDER BY update_date DESC";
        $results = $connection->executeQuery($stmt)->fetchAll();
        return empty($results) ? [] : $results;
    }

    /**
     * @param string $name
     * @return array
     */
    public function getByName(string $name) : array
    {
        $connection = $this->getConnection();
        $stmt = "
            SELECT
                ei.id,
                ei.name,
                ei.tables_prefix,
                ei.track_name,
                ei.event_type,
                ei.update_date
            FROM `" . Tables::EVENTS_INDEX . "` ei
            WHERE ei.name = :name";
        $params = [':name' => $name];
        $results = $connection->executeQuery($stmt, $params)->fetch();
        return empty($results) ? [] : $results;
    }

    /**
     * @param array $row
     * @return void
     */
    public function insert(array $row) : void
    {
        parent::simpleInsert($row, Tables::EVENTS_INDEX);
    }
}
