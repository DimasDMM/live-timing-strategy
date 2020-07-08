<?php
namespace CkmTiming\Storages\v1\SantosEndurance;

use CkmTiming\Enumerations\Tables;

class KartsBoxProbsStorage extends AbstractSantosEnduranceStorage
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
                se_kbp.step,
                se_kbp.kart_status,
                se_kbp.probability,
                se_kbp.update_date
            FROM `" . $tablePrefix . Tables::SE_KARTS_PROBS . "` se_kbp";
        $results = $connection->executeQuery($stmt)->fetchAll();
        $results = array_map(
            function ($row) {
                return [
                    'step' => (int)$row['step'],
                    'kart_status' => $row['kart_status'],
                    'probability' => (float)$row['probability'],
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
        $table = $tablePrefix . Tables::SE_KARTS_PROBS;
        parent::simpleInsert($data, $table);
    }

    /**
     * @param integer $step
     * @param string $kartStatus
     * @param float $probability
     * @return void
     */
    public function updateByStep(int $step, string $kartStatus, float $probability) : void
    {
        $tablePrefix = $this->getTablesPrefix();
        $table = $tablePrefix . Tables::SE_KARTS_PROBS;

        $queryBuilder = $this->getConnection()->createQueryBuilder();
        $queryBuilder
            ->update($table, 'u')
            ->set('u.probability', ':probability')
            ->where(
                $queryBuilder->expr()->andX(
                    $queryBuilder->expr()->eq('step', ':step'),
                    $queryBuilder->expr()->eq('kart_status', ':kart_status')
                )
            )
            ->setParameters([
                ':step' => $step,
                ':kart_status' => $kartStatus,
                ':probability' => $probability,
            ]);

        $queryBuilder->execute();
    }
}
