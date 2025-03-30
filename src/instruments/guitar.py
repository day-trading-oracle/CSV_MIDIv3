"""
Guitar instrument implementation.
"""

from typing import Dict, List, Optional, Tuple
from .base import BaseInstrument, NoteData
from ..utils import normalize_velocity
import logging
import random

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        
        # Store the current song's pattern variation
        self.current_song_variation = None
        
    def get_playable_range(self) -> Tuple[int, int]:
        """Get the playable range of the guitar"""
        return (40, 76)  # E2 to E5
        
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
        Generate a guitar pattern based on the song data.
        
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
        
        # Select pattern variation for new songs
        if is_new_song or self.current_song_variation is None:
            # Define possible variations for guitar patterns
            variations = [
                {
                    'strum_style': 'down',     # Down strums
                    'rhythm': 'quarter',       # Quarter note rhythm
                    'velocity': 85
                },
                {
                    'strum_style': 'alternate',  # Alternate up/down strums
                    'rhythm': 'eighth',         # Eighth note rhythm
                    'velocity': 80
                },
                {
                    'strum_style': 'fingerpick',  # Fingerpicked pattern
                    'rhythm': 'sixteenth',       # Sixteenth note rhythm
                    'velocity': 75
                }
            ]
            self.current_song_variation = random.choice(variations)
            logger.info(f"Selected new variation for guitar: {self.current_song_variation}")
        
        # Use the current song's variation
        pattern_config = self.current_song_variation
        
        logger.info(f"Generating guitar pattern for genre: {genre or 'rock'}")
        logger.info(f"Using pattern configuration: {pattern_config}")
        
        current_time = 0
        for measure in measures:
            chords = measure.get('chords', [])
            melody = measure.get('melody', [])
            
            if not chords and not melody:
                continue
                
            # Handle chords based on pattern variation
            if chords:
                for chord in chords:
                    converted_start = self.convert_to_4_4(chord['start'], original_time_sig)
                    
                    if pattern_config['strum_style'] == 'down':
                        # Down strums
                        note = NoteData(
                            pitch=chord['root'],
                            duration=chord['duration'],
                            start=current_time + converted_start,
                            velocity=normalize_velocity(pattern_config['velocity']),
                            articulation='normal',
                            original_time_sig=original_time_sig
                        )
                        note = self.get_note_adjustments(note, style, genre, original_time_sig)
                        pattern.append({
                            'pitch': note.pitch,
                            'duration': note.duration,
                            'start': note.start,
                            'velocity': note.velocity,
                            'is_rest': note.is_rest,
                            'original_time_sig': note.original_time_sig
                        })
                    elif pattern_config['strum_style'] == 'alternate':
                        # Alternate up/down strums
                        chord_notes = self.get_chord_notes(chord['root'], chord['type'])
                        for i, pitch in enumerate(chord_notes):
                            note = NoteData(
                                pitch=pitch,
                                duration=chord['duration'] / len(chord_notes),
                                start=current_time + converted_start + (i * 0.1),
                                velocity=normalize_velocity(pattern_config['velocity']),
                                articulation='normal',
                                original_time_sig=original_time_sig
                            )
                            note = self.get_note_adjustments(note, style, genre, original_time_sig)
                            pattern.append({
                                'pitch': note.pitch,
                                'duration': note.duration,
                                'start': note.start,
                                'velocity': note.velocity,
                                'is_rest': note.is_rest,
                                'original_time_sig': note.original_time_sig
                            })
                    else:  # fingerpick
                        # Fingerpicked pattern
                        chord_notes = self.get_chord_notes(chord['root'], chord['type'])
                        for i, pitch in enumerate(chord_notes):
                            note = NoteData(
                                pitch=pitch,
                                duration=chord['duration'] / len(chord_notes),
                                start=current_time + converted_start + (i * 0.05),
                                velocity=normalize_velocity(pattern_config['velocity']),
                                articulation='normal',
                                original_time_sig=original_time_sig
                            )
                            note = self.get_note_adjustments(note, style, genre, original_time_sig)
                            pattern.append({
                                'pitch': note.pitch,
                                'duration': note.duration,
                                'start': note.start,
                                'velocity': note.velocity,
                                'is_rest': note.is_rest,
                                'original_time_sig': note.original_time_sig
                            })
            
            # Handle melody
            if melody:
                for note_data in melody:
                    converted_start = self.convert_to_4_4(note_data['start'], original_time_sig)
                    note = NoteData(
                        pitch=note_data['pitch'],
                        duration=note_data['duration'],
                        start=current_time + converted_start,
                        velocity=normalize_velocity(note_data['velocity']),
                        articulation='normal',
                        original_time_sig=original_time_sig
                    )
                    note = self.get_note_adjustments(note, style, genre, original_time_sig)
                    pattern.append({
                        'pitch': note.pitch,
                        'duration': note.duration,
                        'start': note.start,
                        'velocity': note.velocity,
                        'is_rest': note.is_rest,
                        'original_time_sig': note.original_time_sig
                    })
            
            # Move to next measure
            current_time += self.convert_to_4_4(4.0, original_time_sig)
        
        logger.info(f"Generated {len(pattern)} guitar notes")
        return pattern 