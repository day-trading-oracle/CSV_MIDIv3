"""
Drums instrument implementation.
"""

from typing import Dict, List, Optional, Tuple
from .base import BaseInstrument, NoteData
from ..utils import normalize_velocity
import logging
import random

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        
        # Base genre patterns with variations
        self.genre_patterns = {
            'rock': {
                'base': {
                    'kick': [0, 2],  # Beats 1 and 3
                    'snare': [1, 3],  # Beats 2 and 4
                    'hihat': 'eighth',  # Eighth notes
                    'velocity': {'kick': 100, 'snare': 90, 'hihat': 70}
                },
                'variations': [
                    {
                        'kick': [0, 1, 2],  # Add kick on beat 2
                        'snare': [1, 3],
                        'hihat': 'eighth',
                        'velocity': {'kick': 95, 'snare': 90, 'hihat': 70}
                    },
                    {
                        'kick': [0, 2, 3],  # Add kick on beat 4
                        'snare': [1, 3],
                        'hihat': 'eighth',
                        'velocity': {'kick': 100, 'snare': 85, 'hihat': 75}
                    }
                ]
            },
            'jazz': {
                'base': {
                    'kick': [0, 1, 2, 3],  # All beats
                    'snare': [1, 3],  # Beats 2 and 4
                    'hihat': 'sixteenth',  # Sixteenth notes
                    'velocity': {'kick': 85, 'snare': 80, 'hihat': 65}
                },
                'variations': [
                    {
                        'kick': [0, 1, 2, 3],
                        'snare': [1, 2, 3],  # Add snare on beat 3
                        'hihat': 'sixteenth',
                        'velocity': {'kick': 80, 'snare': 75, 'hihat': 60}
                    },
                    {
                        'kick': [0, 1, 2, 3],
                        'snare': [1, 3],
                        'hihat': 'sixteenth',
                        'velocity': {'kick': 90, 'snare': 85, 'hihat': 70}
                    }
                ]
            },
            'funk': {
                'base': {
                    'kick': [0, 1, 2, 3],  # All beats
                    'snare': [1, 3],  # Beats 2 and 4
                    'hihat': 'sixteenth',  # Sixteenth notes
                    'velocity': {'kick': 95, 'snare': 85, 'hihat': 75}
                },
                'variations': [
                    {
                        'kick': [0, 1, 2, 3],
                        'snare': [1, 2, 3],  # Add snare on beat 3
                        'hihat': 'sixteenth',
                        'velocity': {'kick': 100, 'snare': 90, 'hihat': 80}
                    },
                    {
                        'kick': [0, 1, 2, 3],
                        'snare': [1, 3],
                        'hihat': 'sixteenth',
                        'velocity': {'kick': 90, 'snare': 80, 'hihat': 70}
                    }
                ]
            },
            'classical': {
                'base': {
                    'kick': [0, 2],  # Beats 1 and 3
                    'snare': [1, 3],  # Beats 2 and 4
                    'hihat': 'quarter',  # Quarter notes
                    'velocity': {'kick': 80, 'snare': 75, 'hihat': 60}
                },
                'variations': [
                    {
                        'kick': [0, 2],
                        'snare': [1, 3],
                        'hihat': 'eighth',  # More detailed hi-hat
                        'velocity': {'kick': 75, 'snare': 70, 'hihat': 55}
                    },
                    {
                        'kick': [0, 2],
                        'snare': [1, 3],
                        'hihat': 'quarter',
                        'velocity': {'kick': 85, 'snare': 80, 'hihat': 65}
                    }
                ]
            }
        }
        
        # Store the current song's pattern variation
        self.current_song_variation = None
        
    def get_playable_range(self) -> Tuple[int, int]:
        """Get the playable range of the drums"""
        return (35, 81)  # B0 to A2
        
    def generate_pattern(
        self,
        song_data: Dict,
        style: Optional[str] = None,
        genre: Optional[str] = None,
        variation: Optional[int] = None,
        is_new_song: bool = False,
        **kwargs
    ) -> List[Dict]:
        """
        Generate a drum pattern based on the song data.
        
        Args:
            song_data: The song data to generate from
            style: The style of pattern to generate
            genre: The genre of music
            variation: Specific variation to use (None for random)
            is_new_song: Whether this is a new song generation (will select new variation)
            **kwargs: Additional arguments for pattern generation
            
        Returns:
            List of note events
        """
        pattern = []
        measures = song_data.get('measures', [])
        original_time_sig = song_data.get('time_signature', '4/4')
        
        # Get genre-specific pattern or use default
        genre_data = self.genre_patterns.get(genre, self.genre_patterns['rock'])
        
        # Select pattern variation
        if is_new_song or self.current_song_variation is None:
            # For new songs, randomly choose a variation
            all_patterns = [genre_data['base']] + genre_data['variations']
            self.current_song_variation = random.choice(all_patterns)
            logger.info(f"Selected new variation for song: {self.current_song_variation}")
        
        # Use the current song's variation
        pattern_config = self.current_song_variation
        
        logger.info(f"Generating drum pattern for genre: {genre or 'rock'}")
        logger.info(f"Using pattern configuration: {pattern_config}")
        
        current_time = 0
        for measure in measures:
            beats = measure.get('beats', [])
            
            # If no beats specified, create a basic 4/4 pattern
            if not beats:
                beats = [
                    {'position': 0, 'start': 0.0},
                    {'position': 1, 'start': 1.0},
                    {'position': 2, 'start': 2.0},
                    {'position': 3, 'start': 3.0}
                ]
            
            for beat in beats:
                # Convert beat timing to 4/4 time
                converted_start = self.convert_to_4_4(beat['start'], original_time_sig)
                
                # Create drum pattern based on genre
                if beat['position'] in pattern_config['kick']:
                    # Kick drum
                    kick = NoteData(
                        pitch=self.drum_map['kick'],
                        duration=0.1,  # Short duration for drums
                        start=current_time + converted_start,
                        velocity=normalize_velocity(pattern_config['velocity']['kick']),
                        articulation='normal',
                        original_time_sig=original_time_sig
                    )
                    kick = self.get_note_adjustments(kick, style, genre, original_time_sig)
                    pattern.append({
                        'pitch': kick.pitch,
                        'duration': kick.duration,
                        'start': kick.start,
                        'velocity': kick.velocity,
                        'is_rest': kick.is_rest,
                        'original_time_sig': kick.original_time_sig
                    })
                
                if beat['position'] in pattern_config['snare']:
                    # Snare drum
                    snare = NoteData(
                        pitch=self.drum_map['snare'],
                        duration=0.1,
                        start=current_time + converted_start,
                        velocity=normalize_velocity(pattern_config['velocity']['snare']),
                        articulation='normal',
                        original_time_sig=original_time_sig
                    )
                    snare = self.get_note_adjustments(snare, style, genre, original_time_sig)
                    pattern.append({
                        'pitch': snare.pitch,
                        'duration': snare.duration,
                        'start': snare.start,
                        'velocity': snare.velocity,
                        'is_rest': snare.is_rest,
                        'original_time_sig': snare.original_time_sig
                    })
                
                # Hi-hat pattern based on genre
                if pattern_config['hihat'] == 'eighth':
                    subdivisions = 2
                elif pattern_config['hihat'] == 'sixteenth':
                    subdivisions = 4
                else:  # quarter
                    subdivisions = 1
                
                for sub in range(subdivisions):
                    hihat = NoteData(
                        pitch=self.drum_map['hihat'],
                        duration=0.05,  # Very short for hi-hat
                        start=current_time + converted_start + (1.0/subdivisions * sub),
                        velocity=normalize_velocity(pattern_config['velocity']['hihat']),
                        articulation='normal',
                        original_time_sig=original_time_sig
                    )
                    hihat = self.get_note_adjustments(hihat, style, genre, original_time_sig)
                    pattern.append({
                        'pitch': hihat.pitch,
                        'duration': hihat.duration,
                        'start': hihat.start,
                        'velocity': hihat.velocity,
                        'is_rest': hihat.is_rest,
                        'original_time_sig': hihat.original_time_sig
                    })
            
            # Move to next measure
            current_time += self.convert_to_4_4(4.0, original_time_sig)
        
        # If no pattern was generated, create a basic pattern
        if not pattern and measures:
            # Create a basic kick and hi-hat pattern
            pattern.extend([
                {
                    'pitch': self.drum_map['kick'],
                    'duration': 0.1,
                    'start': 0.0,
                    'velocity': pattern_config['velocity']['kick'],
                    'is_rest': False,
                    'original_time_sig': original_time_sig
                },
                {
                    'pitch': self.drum_map['hihat'],
                    'duration': 0.05,
                    'start': 0.0,
                    'velocity': pattern_config['velocity']['hihat'],
                    'is_rest': False,
                    'original_time_sig': original_time_sig
                }
            ])
        
        logger.info(f"Generated {len(pattern)} drum notes")
        return pattern 