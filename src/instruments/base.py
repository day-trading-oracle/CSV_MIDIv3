"""
Base instrument class that defines the common interface for all instruments.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union

@dataclass
class NoteData:
    """Represents a note with its properties."""
    pitch: int
    duration: float
    start: float
    velocity: int
    is_rest: bool = False
    articulation: Optional[str] = None
    effects: Optional[Dict] = None

class BaseInstrument(ABC):
    """Base class for all instruments."""
    
    def __init__(
        self,
        program: int,
        name: str,
        velocity_range: Tuple[int, int] = (30, 120),
        articulations: Optional[Dict[str, Dict[str, float]]] = None,
    ):
        """
        Initialize the instrument.
        
        Args:
            program: MIDI program number
            name: Instrument name
            velocity_range: Tuple of (min_velocity, max_velocity)
            articulations: Dictionary of articulation effects
        """
        self.program = program
        self.name = name
        self.velocity_range = velocity_range
        self.articulations = articulations or {}
    
    @abstractmethod
    def get_playable_range(self) -> Tuple[int, int]:
        """
        Get the playable range of the instrument.
        
        Returns:
            Tuple of (min_pitch, max_pitch) in MIDI note numbers
        """
        pass
    
    def get_note_adjustments(
        self,
        note_data: NoteData,
        style: Optional[str] = None,
        genre: Optional[str] = None
    ) -> NoteData:
        """
        Apply instrument-specific adjustments to a note.
        
        Args:
            note_data: The note to adjust
            style: The style of playing
            genre: The genre of music
            
        Returns:
            Adjusted note data
        """
        # Ensure pitch is within playable range
        min_pitch, max_pitch = self.get_playable_range()
        note_data.pitch = max(min_pitch, min(note_data.pitch, max_pitch))
        
        # Apply articulation effects if specified
        if note_data.articulation and note_data.articulation in self.articulations:
            effects = self.articulations[note_data.articulation]
            note_data.velocity = int(note_data.velocity * effects.get('velocity', 1.0))
            note_data.duration *= effects.get('duration', 1.0)
        
        # Ensure velocity is within range
        note_data.velocity = max(
            self.velocity_range[0],
            min(note_data.velocity, self.velocity_range[1])
        )
        
        return note_data
    
    @abstractmethod
    def generate_pattern(
        self,
        song_data: Dict,
        style: Optional[str] = None,
        genre: Optional[str] = None,
        **kwargs
    ) -> List[Dict]:
        """
        Generate a pattern for this instrument.
        
        Args:
            song_data: The song data to generate from
            style: The style of pattern to generate
            genre: The genre of music
            **kwargs: Additional arguments for pattern generation
            
        Returns:
            List of note events
        """
        pass 