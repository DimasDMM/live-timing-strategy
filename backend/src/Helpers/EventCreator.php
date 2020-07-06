<?php
namespace CkmTiming\Helpers;

use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Exception\HttpBadRequestException;

class EventCreator extends AbstractHelper
{
    const PATH_TEMPLATES = __DIR__ . '/../../artifacts/templates/';

    /** @var Request */
    protected $request;

    /**
     * @param Request $request
     * @return self
     */
    public function setRequest(Request $request) : self
    {
        $this->request = $request;
        return $this;
    }

    /**
     * @param string $trackName
     * @param string $eventType
     * @return bool
     */
    public function isEventSupported(string $trackName, string $eventType) : bool
    {
        return file_exists($this->getTemplatePath($trackName, $eventType));
    }

    /**
     * @param string $eventName
     * @return string
     */
    public function getTablesPrefix(string $eventName) : string
    {
        $fixedName = preg_replace('/[^a-zA-Z_]/', '', $eventName);
        $fixedName = strtolower($fixedName);
        return $fixedName . '_' . hash('crc32', time());
    }

    /**
     * @param string $trackName
     * @param string $eventType
     * @param string $tablesPrefix
     * @return bool
     */
    public function createEventTables(string $trackName, string $eventType, string $tablesPrefix) : bool
    {
        $sqlContent = file_get_contents($this->getTemplatePath($trackName, $eventType));
        $sqlContent = preg_replace('/\{tables_prefix\}/', $tablesPrefix, $sqlContent);

        $connection = $this->getConnection();
        $stmt = $connection->prepare($sqlContent);
        $stmt->execute();

        return true;
    }

    /**
     * @param string $trackName
     * @param string $eventType
     * @return string
     */
    protected function getTemplatePath(string $trackName, string $eventType) : string
    {
        return self::PATH_TEMPLATES . "template_${trackName}_${eventType}.sql";
    }
}
