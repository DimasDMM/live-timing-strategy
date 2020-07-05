<?php
namespace CkmTiming\Storages\v1\Common;

use CkmTiming\Enumerations\Tables;
use CkmTiming\Storages\v1\AbstractStorage;

class EventsIndexStorage extends AbstractStorage
{
    public function getAll() : array
    {
        $connection = $this->getConnection();
        $query = "
            SELECT
                ei.name,
                ei.table_prefix,
                ei.event_type,
                ei.update_date
            FROM " . Tables::EVENTS_INDEX . " ei
            ORDER BY update_date DESC";
        $results = $connection->executeQuery($query)->fetchAll();
        return $results ?? [];
    }
}
