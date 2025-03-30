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
    original_time_sig: Optional[str] = None

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
        
        # Time signature conversion factors
        # These factors are used to scale durations and start times to fit within a 4/4 measure
        self.time_signature_factors = {
            '3/4': 3/4,    # Scale 3 beats to fit in 4 beats
            '6/8': 2/3,    # Scale 6 eighth notes to fit in 4 beats (6/8 = 3/4 in compound time)
            '5/4': 4/5,    # Scale 5 beats to fit in 4 beats
            '7/8': 4/7,    # Scale 7 eighth notes to fit in 4 beats
            '9/8': 4/9,    # Scale 9 eighth notes to fit in 4 beats
            '12/8': 2/3    # Scale 12 eighth notes to fit in 4 beats (12/8 = 4/4 in compound time)
        }
    
    def convert_to_4_4(self, duration: float, original_time_sig: str) -> float:
        """Convert duration from original time signature to 4/4.
        
        Args:
            duration: Original duration in beats
            original_time_sig: Original time signature (e.g., '3/4', '6/8')
            
        Returns:
            Duration converted to 4/4 time
        """
        if original_time_sig in self.time_signature_factors:
            # Scale the duration to fit within a 4/4 measure
            return duration * self.time_signature_factors[original_time_sig]
        return duration  # Default to no conversion if time signature not found
    
    def get_note_adjustments(
        self,
        note_data: NoteData,
        style: Optional[str] = None,
        genre: Optional[str] = None,
        original_time_sig: Optional[str] = None
    ) -> NoteData:
        """
        Apply instrument-specific adjustments to a note.
        
        Args:
            note_data: The note to adjust
            style: The style of playing
            genre: The genre of music
            original_time_sig: Original time signature
            
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
        
        # Store original time signature
        if original_time_sig:
            note_data.original_time_sig = original_time_sig
        
        return note_data
    
    @abstractmethod
    def get_playable_range(self) -> Tuple[int, int]:
        """
        Get the playable range of the instrument.
        
        Returns:
            Tuple of (min_pitch, max_pitch) in MIDI note numbers
        """
        pass
    
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