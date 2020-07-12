<?php
namespace CkmTiming\Storages\v1\SantosEndurance;

use CkmTiming\Enumerations\Tables;

class TimingStorage extends AbstractSantosEnduranceStorage
{
    protected $defaultKartStatus = 'unknown';

    /**
     * @return array
     */
    public function getLastLap() : array
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
                se_d.time_driving driver_time_driving,
                se_th.position,
                se_th.time,
                MAX(se_th.lap) lap,
                se_th.gap,
                se_th.stage,
                se_th.kart_status,
                se_th.kart_status_guess,
                se_th.forced_kart_status,
                se_th.number_stops,
                se_th.is_stop
            FROM `" . $tablePrefix . Tables::SE_TIMING_HISTORIC . "` se_th
            LEFT JOIN `" . $tablePrefix . Tables::SE_TEAMS . "` se_t ON se_t.id = se_th.team_id
            LEFT JOIN `" . $tablePrefix . Tables::SE_DRIVERS . "` se_d ON se_th.driver_id = se_d.id
            GROUP BY se_t.name
            ORDER BY se_th.lap DESC";
        $results = $connection->executeQuery($stmt)->fetchAll();
        $results = empty($results) ? [] : $results;
        $results = $this->castTimingRows($results);
        return $results;
    }

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
                se_d.time_driving driver_time_driving,
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
            LEFT JOIN `" . $tablePrefix . Tables::SE_DRIVERS . "` se_d ON se_th.driver_id = se_d.id
            WHERE se_t.name = :name
            ORDER BY se_th.lap DESC";
        $params = [':name' => $name];
        $results = $connection->executeQuery($stmt, $params)->fetchAll();
        $results = empty($results) ? [] : $results;
        $results = $this->castTimingRows($results);
        return $results;
    }

    /**
     * @param integer $teamId
     * @param integer $numberStops
     * @return array
     */
    public function getLastKnownKartStatus(int $teamId, int $numberStops) : array
    {
        $connection = $this->getConnection();
        $tablePrefix = $this->getTablesPrefix();
        $stmt = "
            SELECT
                se_th.kart_status,
                se_th.kart_status_guess,
                se_th.forced_kart_status,
                se_th.number_stops
            FROM `" . $tablePrefix . Tables::SE_TIMING_HISTORIC . "` se_th
            JOIN `" . $tablePrefix . Tables::SE_TEAMS . "` se_t ON se_t.id = se_th.team_id
            LEFT JOIN `" . $tablePrefix . Tables::SE_DRIVERS . "` se_d ON se_th.driver_id = se_d.id
            WHERE se_t.id = :id
            ORDER BY se_th.insert_date DESC";
        $params = [':id' => $teamId];
        $results = $connection->executeQuery($stmt, $params)->fetch();

        if (empty($results) || $results['number_stops'] != $numberStops) {
            return [];
        }

        return $results;
    }

    /**
     * @param array $data
     * @return void
     */
    public function insert(array $data) : void
    {
        $tablePrefix = $this->getTablesPrefix();
        $table = $tablePrefix . Tables::SE_TIMING_HISTORIC;
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
        $table = $tablePrefix . Tables::SE_TIMING_HISTORIC;
        parent::simpleUpdate($data, $table, $id);
    }

    /**
     * @param array $data
     * @return array
     */
    protected function castTimingRows(array $data) : array
    {
        return array_map(
            function ($row) {
                return [
                    'team_name' => $row['team_name'],
                    'team_number' => (int)$row['team_number'],
                    'team_reference_time_offset' => (int)$row['team_reference_time_offset'],
                    'driver_name' => $row['driver_name'],
                    'driver_reference_time_offset' => isset($row['driver_reference_time_offset']) ? (int)$row['driver_reference_time_offset'] : null,
                    'driver_time_driving' =>  isset($row['driver_time_driving']) ? (int)$row['driver_time_driving'] : null,
                    'position' => (int)$row['position'],
                    'time' => (int)$row['time'],
                    'lap' => (int)$row['lap'],
                    'gap' => (int)$row['gap'],
                    'stage' => $row['stage'],
                    'kart_status' => $row['kart_status'] ?? $this->defaultKartStatus,
                    'kart_status_guess' => $row['kart_status_guess'],
                    'forced_kart_status' => $row['forced_kart_status'],
                    'number_stops' => (int)$row['number_stops'],
                    'is_stop' => (bool)$row['is_stop'],
                ];
            },
            $data
        );
    }
}
