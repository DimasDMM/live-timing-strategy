<?php
namespace CkmTiming\Storages\v1\SantosEndurance;

use CkmTiming\Enumerations\Tables;

class ConfigurationStorage extends AbstractSantosEnduranceStorage
{
    const RACE_LENGTH = 'race_length';
    const RACE_LENGTH_UNIT = 'race_length_unit';
    const REFERENCE_TIME_TOP_TEAMS = 'reference_time_top_teams';
    const MIN_NUMBER_STOPS = 'min_number_stops';
    const STOP_TIME = 'stop_time';

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
            FROM " . $tablePrefix . Tables::SE_EVENT_CONFIG . " ec
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
            FROM `" . $tablePrefix . Tables::SE_EVENT_CONFIG . "` ec
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
            UPDATE `" . $tablePrefix . Tables::SE_EVENT_CONFIG . "`
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
