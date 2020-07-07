<?php
namespace CkmTiming\Storages\v1\SantosEndurance;

use CkmTiming\Enumerations\Tables;

class TimingStorage extends AbstractSantosEnduranceStorage
{
    /**
     * @param string $name
     * @return array
     */
    public function getByTeamName(string $name) : array
    {
        $connection = $this->getConnection();
        $tablePrefix = $this->getTablesPrefix();
        $stmt = "
            SELECT
                se_t.name team_name,
                se_t.number team_number,
                se_t.reference_time_offset team_reference_time_offset,
                se_d.name driver_name,
                se_d.reference_time_offset driver_reference_time_offset,
                se_d.driving_time driver_driving_time,
                se_th.position,
                se_th.time,
                se_th.lap,
                se_th.gap,
                se_th.stage,
                se_th.kart_status,
                se_th.kart_status_guess,
                se_th.forced_kart_status,
                se_th.number_stops,
                se_th.is_stop
            FROM `" . $tablePrefix . Tables::SE_TIMING_HISTORIC . "` se_th
            JOIN `" . $tablePrefix . Tables::SE_TEAMS . "` se_t ON se_t.id = se_th.team_id
            JOIN `" . $tablePrefix . Tables::SE_DRIVERS . "` se_d ON se_t.driver_id = se_d.id
            WHERE se_t.name = :name";
        $params = [':name' => $name];
        $results = $connection->executeQuery($stmt, $params)->fetchAll();
        return empty($results) ? [] : $results;
    }
}
