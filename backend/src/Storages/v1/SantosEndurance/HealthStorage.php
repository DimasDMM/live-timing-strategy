<?php
namespace CkmTiming\Storages\v1\SantosEndurance;

use CkmTiming\Enumerations\Tables;

class HealthStorage extends AbstractSantosEnduranceStorage
{
    const RACE_LENGTH = 'race_length';
    const RACE_LENGTH_UNIT = 'race_length_unit';
    const REFERENCE_TIME_TOP_TEAMS = 'reference_time_top_teams';

    /**
     * @return array
     */
    public function getAll() : array
    {
        $connection = $this->getConnection();
        $tablePrefix = $this->getTablesPrefix();
        $stmt = "
            SELECT
                ec.category,
                ec.name,
                ec.status,
                ec.update_date
            FROM " . $tablePrefix . Tables::SE_EVENT_HEALTH . " ec
            ORDER BY update_date DESC";
        $results = $connection->executeQuery($stmt)->fetchAll();
        return empty($results) ? [] : $results;
    }

    /**
     * @param string $category
     * @param string $name
     * @return array
     */
    public function getByName(string $category, string $name) : array
    {
        $connection = $this->getConnection();
        $tablePrefix = $this->getTablesPrefix();
        $stmt = "
            SELECT
                ec.category,
                ec.name,
                ec.status,
                ec.update_date
            FROM `" . $tablePrefix . Tables::SE_EVENT_HEALTH . "` ec
            WHERE ec.name = :name";
        $params = [':name' => $name];
        $results = $connection->executeQuery($stmt, $params)->fetch();
        return empty($results) ? [] : $results;
    }

    /**
     * @param string $category
     * @param string $name
     * @param string $status
     * @return boolean
     */
    public function updateByName(string $category, string $name, string $status) : bool
    {
        $connection = $this->getConnection();
        $tablePrefix = $this->getTablesPrefix();
        $stmt = "
            UPDATE `" . $tablePrefix . Tables::SE_EVENT_HEALTH . "`
            SET `status` = :status
            WHERE `name` = :name AND `category` = :category";
        $params = [
            ':category' => $category,
            ':name' => $name,
            ':status' => $status,
        ];
        $connection->executeUpdate($stmt, $params);
        return true;
    }
}
