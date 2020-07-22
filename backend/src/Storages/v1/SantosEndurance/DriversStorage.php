<?php
namespace CkmTiming\Storages\v1\SantosEndurance;

use CkmTiming\Enumerations\Tables;

class DriversStorage extends AbstractSantosEnduranceStorage
{
    /**
     * @return array
     */
    public function getAll() : array
    {
        $connection = $this->getConnection();
        $tablePrefix = $this->getTablesPrefix();
        $stmt = "
            SELECT
                se_d.id id,
                se_d.team_id team_id,
                se_d.name name,
                se_d.driving_time,
                se_d.reference_time_offset reference_time_offset,
                se_d.update_date update_date
            FROM `" . $tablePrefix . Tables::SE_DRIVERS . "` se_d";
        $results = $connection->executeQuery($stmt)->fetchAll();
        return empty($results) ? [] : $results;
    }

    /**
     * @param string $name
     * @param int $teamId
     * @return array
     */
    public function getByName(string $name, int $teamId) : array
    {
        $connection = $this->getConnection();
        $tablePrefix = $this->getTablesPrefix();
        $stmt = "
            SELECT
                se_d.id id,
                se_d.team_id team_id,
                se_d.name name,
                se_d.driving_time,
                se_d.reference_time_offset reference_time_offset,
                se_d.update_date update_date
            FROM `" . $tablePrefix . Tables::SE_DRIVERS . "` se_d
            WHERE
                se_d.name = :name AND
                se_d.team_id = :team_id";
        $params = [
            ':name' => $name,
            ':team_id' => $teamId,
        ];
        $results = $connection->executeQuery($stmt, $params)->fetch();
        return empty($results) ? [] : $results;
    }

    /**
     * @param int $teamId
     * @return array
     */
    public function getByTeamId(int $teamId) : array
    {
        $connection = $this->getConnection();
        $tablePrefix = $this->getTablesPrefix();
        $stmt = "
            SELECT
                se_d.id id,
                se_d.name name,
                se_d.driving_time,
                se_d.reference_time_offset reference_time_offset,
                se_d.update_date update_date
            FROM `" . $tablePrefix . Tables::SE_DRIVERS . "` se_d
            JOIN `" . $tablePrefix . Tables::SE_TEAMS . "` se_t ON se_t.id = se_d. team_id
            WHERE se_d.team_id = :team_id";
        $params = [':team_id' => $teamId];
        $results = $connection->executeQuery($stmt, $params)->fetchAll();
        return empty($results) ? [] : $results;
    }

    /**
     * @param array $row
     * @return void
     */
    public function insert(array $row) : void
    {
        $tablePrefix = $this->getTablesPrefix();
        $table = $tablePrefix . Tables::SE_DRIVERS;
        parent::simpleInsert($row, $table);
    }

    /**
     * @param int $id
     * @param array $data
     * @return void
     */
    public function update(int $id, array $data) : void
    {
        $tablePrefix = $this->getTablesPrefix();
        $table = $tablePrefix . Tables::SE_DRIVERS;
        parent::simpleUpdate($data, $table, $id);
    }
}
