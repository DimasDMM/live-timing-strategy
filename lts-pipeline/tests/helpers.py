import os
from unittest.mock import MagicMock

BASE_PATH = 'tests/data/messages'


def build_magic_step() -> MagicMock:
    """Create mock of a step."""
    step = MagicMock()
    step.get_children.return_value = []
    return step


def load_raw_message(filename: str) -> str:
    """Load a raw message."""
    filepath = os.path.join(BASE_PATH, filename)
    with open(filepath, 'r') as fp:
        return fp.read()
