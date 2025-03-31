"""Instrument package initialization."""

from .base import BaseInstrument
from .piano import Piano
from .guitar import Guitar
from .bass import Bass
from .drums import Drums

__all__ = [
    'BaseInstrument',
    'Piano',
    'Guitar',
    'Bass',
    'Drums'
]
