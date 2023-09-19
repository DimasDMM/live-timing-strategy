<?php
/**
 * Basic PSR-Container implementation to speed-up code execution.
 */

namespace LTS\Utils;

use Psr\Container\ContainerInterface;

class BasicContainer implements ContainerInterface
{
    protected $vars;

    /**
     * @inheritDoc
     */
    public function set($id, $value)
    {
        $this->vars[$id] = $value;
        return $this;
    }

    /**
     * @inheritDoc
     */
    public function get(string $id)
    {
        if ($this->has($id)) {
            return $this->vars[$id] instanceof \Closure ? $this->vars[$id]($this) : $this->vars[$id];
        } else {
            return null;
        }
    }

    /**
     * @inheritDoc
     */
    public function has(string $id): bool
    {
        return isset($this->vars[$id]);
    }
}
