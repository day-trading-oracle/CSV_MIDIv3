"""
MusicMidi package for MIDI file generation and manipulation.
"""

from .midi_generator import generate_midi
from .accompaniment_generator import AccompanimentGenerator, GenreManager

__all__ = ['generate_midi', 'AccompanimentGenerator', 'GenreManager'] 