<?php
namespace CkmTiming\Storages\v1\SantosEndurance;

use CkmTiming\Enumerations\Tables;

class TimingStorage extends AbstractSantosEnduranceStorage
{
    protected $defaultKartStatus = 'unknown';

    /**
     * @param bool $orderFirstPosition Optional
     * @return array
     */
    public function getLastLap($orderFirstPosition = true) : array
    {
        $orderClause = $orderFirstPosition
            ? 'ORDER BY se_t.position ASC, se_t.lap DESC'
            : 'ORDER BY se_t.lap DESC, se_t.position ASC';

        $connection = $this->getConnection();
        $tablePrefix = $this->getTablesPrefix();
        $stmt = "
            SELECT *
            FROM (
                SELECT
                    se_t.name team_name,
                    se_t.number team_number,
                    se_t.reference_time_offset team_reference_time_offset,
                    se_d.name driver_name,
                    se_d.reference_time_offset driver_reference_time_offset,
                    se_d.driving_time driver_driving_time,
                    se_th.position,
                    se_th.time,
                    se_th.best_time,
                    se_th.lap,
                    se_th.interval,
                    se_th.interval_unit,
                    se_th.stage,
                    se_th.kart_status,
                    se_th.kart_status_guess,
                    se_th.forced_kart_status,
                    se_th.number_stops,
                    se_th.is_stop
                FROM `" . $tablePrefix . Tables::SE_TIMING_HISTORIC . "` se_th
                LEFT JOIN `" . $tablePrefix . Tables::SE_TEAMS . "` se_t ON se_t.id = se_th.team_id
                LEFT JOIN `" . $tablePrefix . Tables::SE_DRIVERS . "` se_d ON se_th.driver_id = se_d.id
                ORDER BY se_th.insert_date DESC
            ) se_t
            GROUP BY se_t.team_name
            $orderClause";
        $results = $connection->executeQuery($stmt)->fetchAll();
        $results = empty($results) ? [] : $results;
        $results = $this->castTimingRows($results);
        $results = $this->getFixedPositions($results);
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
                se_d.driving_time driver_driving_time,
                se_th.position,
                se_th.time,
                se_th.best_time,
                se_th.lap,
                se_th.interval,
                se_th.interval_unit,
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
            ORDER BY se_th.lap ASC";
        $params = [':name' => $name];
        $results = $connection->executeQuery($stmt, $params)->fetchAll();
        $results = empty($results) ? [] : $results;
        $results = $this->castTimingRows($results);
        return $results;
    }

    /**
     * @param integer $teamId
     * @param integer $numberStops Optional
     * @return array
     */
    public function getLastKnownKartStatus(int $teamId, int $numberStops = null) : array
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

        if (empty($results) || (!is_null($numberStops) && $results['number_stops'] != $numberStops)) {
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
     * @param int $teamId
     * @param string $stage
     * @param int $lap
     * @param array $data
     * @return void
     */
    public function updateByTeamStageLap(int $teamId, string $stage, int $lap, array $data) : void
    {
        $tablePrefix = $this->getTablesPrefix();
        
        $queryBuilder = $this->getConnection()->createQueryBuilder();
        $queryBuilder->update($tablePrefix . Tables::SE_TIMING_HISTORIC, 'u');

        foreach ($data as $column => $value) {
            $paramName = ':' . $column;
            $queryBuilder
                ->set("u.$column", $paramName)
                ->setParameter($column, $value);
        }

        $queryBuilder->where('u.team_id = :team_id AND u.stage = :stage AND u.lap = :lap');
        $queryBuilder->setParameters([
            ':team_id' => $teamId,
            ':stage' => $stage,
            ':lap' => $lap,
        ]);

        $queryBuilder->execute();
    }

    /**
     * @param string $stage
     * @param int $teamId
     * @param int $numberStops
     * @param string $forcedKartStatus
     * @return void
     */
    public function updateLastKartStatus(
        string $stage,
        int $teamId,
        int $numberStops,
        string $forcedKartStatus = null
    ) : void {
        $connection = $this->getConnection();
        $tablePrefix = $this->getTablesPrefix();
        $stmt = "
            UPDATE `" . $tablePrefix . Tables::SE_TIMING_HISTORIC . "`
            SET `forced_kart_status` = :forced_kart_status
            WHERE
                `stage` = :stage AND
                `team_id` = :team_id AND
                `number_stops` = :number_stops";
        $params = [
            ':stage' => $stage,
            ':team_id' => $teamId,
            ':number_stops' => $numberStops,
            ':forced_kart_status' => $forcedKartStatus,
        ];
        $connection->executeUpdate($stmt, $params);
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
                    'driver_driving_time' => isset($row['driver_driving_time']) ? (int)$row['driver_driving_time'] : null,
                    'position' => (int)$row['position'],
                    'time' => (int)$row['time'],
                    'best_time' => (int)$row['best_time'],
                    'lap' => (int)$row['lap'],
                    'interval' => (int)$row['interval'],
                    'interval_unit' => $row['interval_unit'],
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

    /**
     * @param array $data
     * @return array
     */
    protected function getFixedPositions(array $data) : array
    {
        $i = 0;
        foreach ($data as &$row) {
            $i++;
            $row['position'] = $i;
        }
        return $data;
    }
}
