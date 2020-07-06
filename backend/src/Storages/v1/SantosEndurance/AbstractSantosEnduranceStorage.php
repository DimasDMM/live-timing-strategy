<?php
namespace CkmTiming\Storages\v1\SantosEndurance;

use CkmTiming\Storages\v1\AbstractStorage;

abstract class AbstractSantosEnduranceStorage extends AbstractStorage
{
    /** @var string */
    protected $tablesPrefix;

    /**
     * @return string $tablesPrefix
     */
    public function setTablesPrefix($tablesPrefix) : self
    {
        $this->tablesPrefix = $tablesPrefix;
        return $this;
    }

    /**
     * @return string
     */
    public function getTablesPrefix() : string
    {
        if (is_null($this->tablesPrefix)) {
            return $this->container->get('tables_prefix');
        }
        return $this->tablesPrefix;
    }
}
