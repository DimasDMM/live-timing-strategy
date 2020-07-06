<?php
namespace CkmTiming\Storages\v1\SantosEndurance;

use CkmTiming\Enumerations\Tables;

class EventStatsStorage extends AbstractSantosEnduranceStorage
{
    const REFERENCE_CURRENT_OFFSET = 'reference_current_offset';
    const REFERENCE_TIME = 'reference_time';
    const REMAINING_EVENT = 'remaining_event';
    const STAGE = 'stage';
    const STATUS = 'status';

    /**
     * @return array
     */
    public function getAll() : array
    {
        $connection = $this->getConnection();
        $tablePrefix = $this->getTablesPrefix();
        $stmt = "
            SELECT
                ec.name,
                ec.value,
                ec.update_date
            FROM " . $tablePrefix . Tables::SE_EVENT_STATS . " ec
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
        $tablePrefix = $this->getTablesPrefix();
        $stmt = "
            SELECT
                ec.name,
                ec.value,
                ec.update_date
            FROM `" . $tablePrefix . Tables::SE_EVENT_STATS . "` ec
            WHERE ec.name = :name";
        $params = [':name' => $name];
        $results = $connection->executeQuery($stmt, $params)->fetch();
        return empty($results) ? [] : $results;
    }

    /**
     * @param string $name
     * @param string $value
     * @return boolean
     */
    public function updateByName(string $name, string $value) : bool
    {
        $connection = $this->getConnection();
        $tablePrefix = $this->getTablesPrefix();
        $stmt = "
            UPDATE `" . $tablePrefix . Tables::SE_EVENT_STATS . "`
            SET `value` = :value
            WHERE `name` = :name";
        $params = [
            ':name' => $name,
            ':value' => $value,
        ];
        $connection->executeUpdate($stmt, $params);
        return true;
    }
}
