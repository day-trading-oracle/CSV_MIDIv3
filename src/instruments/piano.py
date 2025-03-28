"""
Piano instrument implementation.
"""

from typing import Dict, List, Optional, Tuple
from .base import BaseInstrument, NoteData
from ..utils import normalize_velocity

class Piano(BaseInstrument):
    """Piano instrument class."""
    
    def __init__(
        self,
        program: int = 0,  # Acoustic Grand Piano
        velocity_range: Tuple[int, int] = (30, 120),
        articulations: Optional[Dict[str, Dict[str, float]]] = None,
    ):
        """
        Initialize the piano.
        
        Args:
            program: MIDI program number (default: Acoustic Grand Piano)
            velocity_range: Tuple of (min_velocity, max_velocity)
            articulations: Dictionary of articulation effects
        """
        super().__init__(
            program=program,
            name="Piano",
            velocity_range=velocity_range,
            articulations=articulations
        )
        
    def get_playable_range(self) -> Tuple[int, int]:
        """Get the playable range of the piano"""
        return (21, 108)  # A0 to C8
        
    def generate_pattern(
        self,
        song_data: Dict,
        style: Optional[str] = None,
        genre: Optional[str] = None,
        **kwargs
    ) -> List[Dict]:
        """
        Generate a piano pattern based on the song data.
        
        Args:
            song_data: The song data to generate from
            style: The style of pattern to generate
            genre: The genre of music
            **kwargs: Additional arguments for pattern generation
            
        Returns:
            List of note events
        """
        pattern = []
        melody = song_data.get('melody', [])
        
        for note in melody:
            note_data = NoteData(
                pitch=note['pitch'],
                duration=note['duration'],
                start=note['start'],
                velocity=normalize_velocity(note.get('velocity', 100)),
                articulation=note.get('articulation')
            )
            
            # Apply instrument-specific adjustments
            note_data = self.get_note_adjustments(note_data, style, genre)
            
            pattern.append({
                'pitch': note_data.pitch,
                'duration': note_data.duration,
                'start': note_data.start,
                'velocity': note_data.velocity,
                'is_rest': note_data.is_rest
            })
        
        return pattern 