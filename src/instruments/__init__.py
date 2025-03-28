"""
Instruments package for MIDI music generation.
"""

from .base import BaseInstrument, NoteData
from .piano import Piano
from .bass import Bass
from .drums import Drums
from .guitar import Guitar
from .instrument_manager import InstrumentManager

__all__ = [
    'BaseInstrument',
    'NoteData',
    'Piano',
    'Bass',
    'Drums',
    'Guitar',
    'InstrumentManager',
] 