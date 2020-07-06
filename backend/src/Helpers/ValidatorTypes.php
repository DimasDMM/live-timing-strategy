<?php
namespace CkmTiming\Helpers;

use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Exception\HttpBadRequestException;

class ValidatorTypes extends AbstractHelper
{
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
     * @param string $paramName
     * @param mixed $value
     * @return void
     * @throws HttpBadRequestException
     */
    public function isNull(string $paramName, $value) : void
    {
        if (is_null($value)) {
            throw new HttpBadRequestException($this->request, "Param $paramName is not set.");
        }
    }

    /**
     * @param string $paramName
     * @param mixed $value
     * @return void
     * @throws HttpBadRequestException
     */
    public function empty(string $paramName, $value) : void
    {
        if (empty($value)) {
            throw new HttpBadRequestException($this->request, "Param $paramName is empty.");
        }
    }

    /**
     * @param string $paramName
     * @param mixed $value
     * @return void
     * @throws HttpBadRequestException
     */
    public function isArray(string $paramName, $value) : void
    {
        if (!is_array($value)) {
            throw new HttpBadRequestException($this->request, "Param $paramName must be an array.");
        }
    }

    /**
     * @param string $paramName
     * @param mixed $value
     * @return void
     * @throws HttpBadRequestException
     */
    public function isString(string $paramName, $value) : void
    {
        if (!is_string($value)) {
            throw new HttpBadRequestException($this->request, "Param $paramName must be a string.");
        }
    }

    /**
     * @param string $paramName
     * @param mixed $value
     * @return void
     * @throws HttpBadRequestException
     */
    public function isInteger(string $paramName, $value) : void
    {
        if (!is_integer($value)) {
            throw new HttpBadRequestException($this->request, "Param $paramName must be an integer.");
        }
    }

    /**
     * @param string $paramName
     * @param mixed $value
     * @return void
     * @throws HttpBadRequestException
     */
    public function isNumeric(string $paramName, $value) : void
    {
        if (!is_numeric($value)) {
            throw new HttpBadRequestException($this->request, "Param $paramName must be a numeric.");
        }
    }
}
