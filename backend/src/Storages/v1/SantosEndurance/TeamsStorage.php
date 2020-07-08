<?php
namespace CkmTiming\Storages\v1\SantosEndurance;

use CkmTiming\Enumerations\Tables;

class TeamsStorage extends AbstractSantosEnduranceStorage
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
                se_t.id id,
                se_t.name name,
                se_t.number number,
                se_t.reference_time_offset reference_time_offset,
                se_t.update_date update_date
            FROM `" . $tablePrefix . Tables::SE_TEAMS . "` se_t";
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
                se_t.id id,
                se_t.name name,
                se_t.number number,
                se_t.reference_time_offset reference_time_offset,
                se_t.update_date update_date
            FROM `" . $tablePrefix . Tables::SE_TEAMS . "` se_t
            WHERE se_t.name = :name";
        $params = [':name' => $name];
        $results = $connection->executeQuery($stmt, $params)->fetch();
        return empty($results) ? [] : $results;
    }

    /**
     * @param array $data
     * @return void
     */
    public function insert(array $data) : void
    {
        $tablePrefix = $this->getTablesPrefix();
        $table = $tablePrefix . Tables::SE_TEAMS;
        parent::simpleInsert($data, $table);
    }

    /**
     * @param int $id
     * @param array $data
     * @return void
     */
    public function update(int $id, array $data) : void
    {
        $tablePrefix = $this->getTablesPrefix();
        $table = $tablePrefix . Tables::SE_TEAMS;
        parent::simpleUpdate($data, $table, $id);
    }
}
