"""
Drums instrument implementation.
"""

from typing import Dict, List, Optional, Tuple
from .base import BaseInstrument, NoteData
from ..utils import normalize_velocity

class Drums(BaseInstrument):
    """Drums instrument class."""
    
    def __init__(
        self,
        program: int = 128,  # Standard Kit
        velocity_range: Tuple[int, int] = (30, 120),
        articulations: Optional[Dict[str, Dict[str, float]]] = None,
    ):
        """
        Initialize the drums.
        
        Args:
            program: MIDI program number (default: Standard Kit)
            velocity_range: Tuple of (min_velocity, max_velocity)
            articulations: Dictionary of articulation effects
        """
        super().__init__(
            program=program,
            name="Drums",
            velocity_range=velocity_range,
            articulations=articulations
        )
        
        # Standard drum kit mapping (MIDI note numbers)
        self.drum_map = {
            'kick': 36,    # C1
            'snare': 38,   # D1
            'hihat': 42,   # F#1
            'tom1': 45,    # A1
            'tom2': 47,    # B1
            'crash': 49,   # C#2
            'ride': 51,    # D#2
        }
        
    def get_playable_range(self) -> Tuple[int, int]:
        """Get the playable range of the drums"""
        return (35, 81)  # B0 to A2
        
    def generate_pattern(
        self,
        song_data: Dict,
        style: Optional[str] = None,
        genre: Optional[str] = None,
        **kwargs
    ) -> List[Dict]:
        """
        Generate a drum pattern based on the song data.
        
        Args:
            song_data: The song data to generate from
            style: The style of pattern to generate
            genre: The genre of music
            **kwargs: Additional arguments for pattern generation
            
        Returns:
            List of note events
        """
        pattern = []
        beats = song_data.get('beats', [])
        
        for beat in beats:
            # Create basic drum pattern
            if beat['position'] == 0:  # On the beat
                # Kick drum
                kick = NoteData(
                    pitch=self.drum_map['kick'],
                    duration=0.1,  # Short duration for drums
                    start=beat['start'],
                    velocity=normalize_velocity(100),
                    articulation='normal'
                )
                pattern.append({
                    'pitch': kick.pitch,
                    'duration': kick.duration,
                    'start': kick.start,
                    'velocity': kick.velocity,
                    'is_rest': kick.is_rest
                })
                
                # Snare drum
                if beat['position'] % 2 == 0:  # Every other beat
                    snare = NoteData(
                        pitch=self.drum_map['snare'],
                        duration=0.1,
                        start=beat['start'],
                        velocity=normalize_velocity(90),
                        articulation='normal'
                    )
                    pattern.append({
                        'pitch': snare.pitch,
                        'duration': snare.duration,
                        'start': snare.start,
                        'velocity': snare.velocity,
                        'is_rest': snare.is_rest
                    })
            
            # Hi-hat on every eighth note
            hihat = NoteData(
                pitch=self.drum_map['hihat'],
                duration=0.05,  # Very short for hi-hat
                start=beat['start'],
                velocity=normalize_velocity(70),
                articulation='normal'
            )
            pattern.append({
                'pitch': hihat.pitch,
                'duration': hihat.duration,
                'start': hihat.start,
                'velocity': hihat.velocity,
                'is_rest': hihat.is_rest
            })
        
        return pattern 