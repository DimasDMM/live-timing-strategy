<?php
namespace CkmTiming\Storages\v1\SantosEndurance;

use CkmTiming\Enumerations\Tables;

class KartsBoxInStorage extends AbstractSantosEnduranceStorage
{
    /**
     * @param int $limit Optional
     * @return array
     */
    public function getAll(int $limit = null) : array
    {
        $connection = $this->getConnection();
        $tablePrefix = $this->getTablesPrefix();
        $stmt = "
            SELECT
                se_kbi.team_id,
                se_t.name team_name,
                se_kbi.kart_status,
                se_kbi.forced_kart_status,
                se_kbi.update_date
            FROM `" . $tablePrefix . Tables::SE_KARTS_IN . "` se_kbi
            JOIN `" . $tablePrefix . Tables::SE_TEAMS . "` se_t ON se_t.id = se_kbi.team_id
            ORDER BY se_kbi.update_date DESC";
        
        if (!is_null($limit)) {
            $stmt .= " LIMIT $limit";
        }
        
        $results = $connection->executeQuery($stmt)->fetchAll();
        $results = array_map(
            function ($row) {
                return [
                    'team_name' => $row['team_name'],
                    'kart_status' => $row['kart_status'],
                    'forced_kart_status' => $row['forced_kart_status'],
                    'update_date' => $row['update_date'],
                ];
            },
            $results
        );

        return empty($results) ? [] : $results;
    }

    /**
     * @param array $data
     * @return void
     */
    public function insert(array $data) : void
    {
        $tablePrefix = $this->getTablesPrefix();
        $table = $tablePrefix . Tables::SE_KARTS_IN;
        parent::simpleInsert($data, $table);
    }
}
