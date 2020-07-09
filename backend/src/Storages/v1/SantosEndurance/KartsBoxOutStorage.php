<?php
namespace CkmTiming\Storages\v1\SantosEndurance;

use CkmTiming\Enumerations\Tables;

class KartsBoxOutStorage extends AbstractSantosEnduranceStorage
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
                se_kbo.team_id,
                se_t.name team_name,
                se_kbo.kart_status,
                se_kbo.forced_kart_status,
                se_kbo.update_date
            FROM `" . $tablePrefix . Tables::SE_KARTS_OUT . "` se_kbo
            JOIN `" . $tablePrefix . Tables::SE_TEAMS . "` se_t ON se_t.id = se_kbo.team_id
            ORDER BY se_kbo.update_date DESC";
        
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
        $table = $tablePrefix . Tables::SE_KARTS_OUT;
        parent::simpleInsert($data, $table);
    }
}
