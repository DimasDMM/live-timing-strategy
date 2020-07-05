<?php
namespace CkmTiming\Helpers;

use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Exception\HttpBadRequestException;

class ValidatorRanges extends AbstractHelper
{
    /** @var Request */
    protected $request;

    protected $trackNames = ['santos'];
    protected $raceTypes = ['endurance'];
    protected $raceLengthUnits = ['laps', 'hours'];

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
     * @param string $paramName
     * @param mixed $value
     * @param bool $includeZero Optional
     * @return void
     * @throws HttpBadRequestException
     */
    public function isPositiveNumber(string $paramName, $value, $includeZero = false) : void
    {
        if ($value < 0 || (!$includeZero && $value == 0)) {
            throw new HttpBadRequestException($this->request, "Param $paramName must be a positive number.");
        }
    }

    /**
     * @param string $paramName
     * @param mixed $value
     * @return void
     * @throws HttpBadRequestException
     */
    public function isValidTrackName(string $paramName, $value)
    {
        if (!in_array($value, $this->trackNames)) {
            throw new HttpBadRequestException($this->request, "Param $paramName is not a valid track name.");
        }
    }

    /**
     * @param string $paramName
     * @param mixed $value
     * @return void
     * @throws HttpBadRequestException
     */
    public function isValidRaceType(string $paramName, $value)
    {
        if (!in_array($value, $this->raceTypes)) {
            throw new HttpBadRequestException($this->request, "Param $paramName is not a valid race type.");
        }
    }

    /**
     * @param string $paramName
     * @param mixed $value
     * @return void
     * @throws HttpBadRequestException
     */
    public function isValidRaceLengthUnit(string $paramName, $value)
    {
        if (!in_array($value, $this->raceLengthUnits)) {
            throw new HttpBadRequestException($this->request, "Param $paramName is not a valid race length unit.");
        }
    }

}
