<?php
/**
 * Basic PSR-Container implementation to speed-up code execution.
 */

namespace LTS\Utils;

use Psr\Container\ContainerInterface;

class BasicContainer implements ContainerInterface
{
    /**
     * @inheritDoc
     */
    public function set($name, $value)
    {
        $this->vars[$name] = $value;
        return $this;
    }

    /**
     * @inheritDoc
     */
    public function get($name)
    {
        if ($this->has($name)) {
            return $this->vars[$name] instanceof \Closure ? $this->vars[$name]($this) : $this->vars[$name];
        } else {
            return null;
        }
    }

    /**
     * @inheritDoc
     */
    public function has($name)
    {
        return isset($this->vars[$name]);
    }
}
