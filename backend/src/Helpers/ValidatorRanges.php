<?php
namespace CkmTiming\Helpers;

use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Exception\HttpBadRequestException;

class ValidatorRanges extends AbstractHelper
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
     * @param array $set
     * @return void
     * @throws HttpBadRequestException
     */
    public function inArray(string $paramName, $value, array $set)
    {
        if (!in_array($value, $set)) {
            throw new HttpBadRequestException($this->request, "Param $paramName has not a valid value.");
        }
    }

    /**
     * @param string $paramName
     * @param mixed $items
     * @param array $expectedAttributes
     * @return void
     * @throws HttpBadRequestException
     */
    public function itemsHasAttributes(string $paramName, $items, array $expectedAttributes) : void
    {
        $mandatory = [];
        foreach ($expectedAttributes as $attrName => $isMandatory) {
            if ($isMandatory) {
                $mandatory[] = $attrName;
            }
        }

        foreach ($items as $item) {
            $intersect = array_intersect(array_keys($item), array_keys($mandatory));
            if (!empty($intersect)) {
                throw new HttpBadRequestException($this->request, "There are missing mandatory attributes in the param $paramName.");
            }
            
            foreach (array_keys($item) as $attrName) {
                if (!isset($expectedAttributes[$attrName])) {
                    throw new HttpBadRequestException($this->request, "There are unknown attributes in the param $paramName.");
                }
            }
        }
    }
}
