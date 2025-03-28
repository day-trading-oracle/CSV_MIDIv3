"""
Guitar instrument implementation.
"""

from typing import Dict, List, Optional, Tuple
from .base import BaseInstrument, NoteData
from ..utils import normalize_velocity

class Guitar(BaseInstrument):
    """Guitar instrument class."""
    
    def __init__(
        self,
        program: int = 24,  # Acoustic Guitar (nylon)
        velocity_range: Tuple[int, int] = (30, 120),
        articulations: Optional[Dict[str, Dict[str, float]]] = None,
    ):
        """
        Initialize the guitar.
        
        Args:
            program: MIDI program number (default: Acoustic Guitar)
            velocity_range: Tuple of (min_velocity, max_velocity)
            articulations: Dictionary of articulation effects
        """
        super().__init__(
            program=program,
            name="Guitar",
            velocity_range=velocity_range,
            articulations=articulations
        )
        
    def get_playable_range(self) -> Tuple[int, int]:
        """Get the playable range of the guitar"""
        return (40, 76)  # E2 to E5
        
    def generate_pattern(
        self,
        song_data: Dict,
        style: Optional[str] = None,
        genre: Optional[str] = None,
        **kwargs
    ) -> List[Dict]:
        """
        Generate a guitar pattern based on the song data.
        
        Args:
            song_data: The song data to generate from
            style: The style of pattern to generate
            genre: The genre of music
            **kwargs: Additional arguments for pattern generation
            
        Returns:
            List of note events
        """
        pattern = []
        chords = song_data.get('chords', [])
        
        for chord in chords:
            # Get chord components
            root = chord['root']
            chord_type = chord.get('type', 'major')
            
            # Create chord notes
            if chord_type == 'major':
                notes = [root, root + 4, root + 7]  # Major triad
            elif chord_type == 'minor':
                notes = [root, root + 3, root + 7]  # Minor triad
            else:
                notes = [root, root + 4, root + 7]  # Default to major
            
            # Create guitar chord pattern
            for note in notes:
                # Create note data
                note_data = NoteData(
                    pitch=note,
                    duration=chord['duration'],
                    start=chord['start'],
                    velocity=normalize_velocity(80),
                    articulation='normal'
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