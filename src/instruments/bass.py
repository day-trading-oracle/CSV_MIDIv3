"""
Bass instrument implementation with bass-specific music theory and patterns.
"""

from typing import Dict, List, Optional, Tuple
from .base import BaseInstrument, NoteData
from ..utils import normalize_velocity
import logging
import random

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Bass(BaseInstrument):
    """Bass instrument implementation with bass-specific patterns and theory"""
    
    def __init__(self, program: int = 32, velocity_range: Tuple[int, int] = (30, 120)):
        """Initialize the bass instrument.
        
        Args:
            program: MIDI program number (default: 32 for Acoustic Bass)
            velocity_range: Min/max velocity values for note dynamics
        """
        articulations = {
            'staccato': {'duration_multiplier': 0.5},
            'legato': {'duration_multiplier': 1.2},
            'pizzicato': {'velocity_multiplier': 1.2},
            'slap': {'velocity_multiplier': 1.5, 'duration_multiplier': 0.8}
        }
        super().__init__(program, "Bass", velocity_range, articulations)
        
        # Bass-specific note ranges (in MIDI note numbers)
        self.range_by_style = {
            'classical': (28, 55),    # E1 to G3
            'jazz': (24, 55),         # C1 to G3
            'rock': (28, 55),         # E1 to G3
            'funk': (28, 55),         # E1 to G3
            'pop': (28, 55)           # E1 to G3
        }
        
        # Bass-specific patterns
        self.patterns = {
            'walking': self._create_walking_pattern,
            'rock': self._create_rock_pattern,
            'funk': self._create_funk_pattern,
            'jazz': self._create_jazz_pattern,
            'pop': self._create_pop_pattern
        }
        
        # Bass-specific chord progressions
        self.chord_progressions = {
            'classical': [
                [0, 4, 7],    # C major
                [2, 5, 9],    # D minor
                [4, 7, 11],   # E minor
                [5, 9, 0],    # F major
                [7, 11, 2],   # G major
                [9, 0, 4],    # A minor
                [11, 2, 5]    # B diminished
            ],
            'jazz': [
                [0, 4, 7, 11],    # Cmaj7
                [2, 5, 9, 0],     # Dm7
                [4, 7, 11, 2],    # Em7
                [5, 9, 0, 4],     # Fmaj7
                [7, 11, 2, 5],    # G7
                [9, 0, 4, 7],     # Am7
                [11, 2, 5, 9]     # Bm7b5
            ],
            'pop': [
                [0, 4, 7],    # C major
                [5, 9, 0],    # F major
                [7, 11, 2],   # G major
                [0, 4, 7]     # C major
            ]
        }
        
        # Store the current song's pattern variation
        self.current_song_variation = None
    
    def get_playable_range(self) -> Tuple[int, int]:
        """Get the playable range for the bass instrument."""
        return (24, 55)  # C1 to G3
    
    def get_chord_progression(self, genre: str) -> List[List[int]]:
        """Get the chord progression for a specific genre.
        
        Args:
            genre: The genre to get the progression for
            
        Returns:
            List of chord definitions (each chord is a list of intervals)
            
        Raises:
            ValueError: If genre is not supported
        """
        if genre not in self.chord_progressions:
            raise ValueError(f"Unsupported genre: {genre}")
        return self.chord_progressions[genre]
    
    def _create_walking_pattern(self, chord: List[int], duration: float) -> List[NoteData]:
        """Create a walking bass pattern."""
        pattern = []
        # Adjust number of steps based on duration
        steps = [0, 2, 4, 5, 7, 9, 11, 12]  # Scale degrees
        step_duration = duration / len(steps)
        
        for i, step in enumerate(steps):
            note = NoteData(
                pitch=chord[0] + step,  # Root note + scale degree
                duration=step_duration,
                start=i * step_duration,
                velocity=80
            )
            pattern.append(note)
        
        return pattern
    
    def _create_rock_pattern(self, chord: List[int], duration: float) -> List[NoteData]:
        """Create a rock bass pattern."""
        pattern = []
        # Root note on 1 and 3
        pattern.append(NoteData(pitch=chord[0], duration=duration/2, start=0, velocity=90))
        pattern.append(NoteData(pitch=chord[0], duration=duration/2, start=duration/2, velocity=90))
        return pattern
    
    def _create_funk_pattern(self, chord: List[int], duration: float) -> List[NoteData]:
        """Create a funk bass pattern."""
        pattern = []
        # Syncopated pattern with root and fifth
        pattern.append(NoteData(pitch=chord[0], duration=duration/4, start=0, velocity=100))
        pattern.append(NoteData(pitch=chord[0] + 7, duration=duration/4, start=duration/4, velocity=90))
        pattern.append(NoteData(pitch=chord[0], duration=duration/4, start=duration/2, velocity=100))
        pattern.append(NoteData(pitch=chord[0] + 7, duration=duration/4, start=3*duration/4, velocity=90))
        return pattern
    
    def _create_jazz_pattern(self, chord: List[int], duration: float) -> List[NoteData]:
        """Create a jazz bass pattern."""
        pattern = []
        # Walking pattern with chord tones
        steps = [chord[0], chord[1], chord[2], chord[0]]  # Root, third, fifth, root
        step_duration = duration / len(steps)
        
        for i, pitch in enumerate(steps):
            note = NoteData(
                pitch=pitch,
                duration=step_duration,
                start=i * step_duration,
                velocity=85
            )
            pattern.append(note)
        
        return pattern
    
    def _create_pop_pattern(self, chord: List[int], duration: float) -> List[NoteData]:
        """Create a pop bass pattern."""
        pattern = []
        # Simple root-fifth pattern
        pattern.append(NoteData(pitch=chord[0], duration=duration/2, start=0, velocity=85))
        pattern.append(NoteData(pitch=chord[0] + 7, duration=duration/2, start=duration/2, velocity=85))
        return pattern
    
    def convert_to_4_4(self, duration: float, original_time_sig: str) -> float:
        """Convert duration from original time signature to 4/4.
        
        Args:
            duration: Original duration in beats
            original_time_sig: Original time signature (e.g., '3/4', '6/8')
            
        Returns:
            Duration converted to 4/4 time
        """
        if original_time_sig in self.time_signature_factors:
            return duration * self.time_signature_factors[original_time_sig]
        return duration  # Default to no conversion if time signature not found

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
        Generate a bass pattern based on the song data.
        
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
            # Define possible variations for bass patterns
            variations = [
                {
                    'style': 'root',      # Root notes only
                    'rhythm': 'quarter',   # Quarter note rhythm
                    'velocity': 90
                },
                {
                    'style': 'walking',    # Walking bass line
                    'rhythm': 'eighth',    # Eighth note rhythm
                    'velocity': 85
                },
                {
                    'style': 'groove',     # Groove-based pattern
                    'rhythm': 'sixteenth', # Sixteenth note rhythm
                    'velocity': 80
                }
            ]
            self.current_song_variation = random.choice(variations)
            logger.info(f"Selected new variation for bass: {self.current_song_variation}")
        
        # Use the current song's variation
        pattern_config = self.current_song_variation
        
        logger.info(f"Generating bass pattern for genre: {genre or 'rock'}")
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
                    
                    if pattern_config['style'] == 'root':
                        # Root notes only
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
                    elif pattern_config['style'] == 'walking':
                        # Walking bass line
                        chord_notes = self.get_chord_notes(chord['root'], chord['type'])
                        for i, pitch in enumerate(chord_notes):
                            note = NoteData(
                                pitch=pitch,
                                duration=chord['duration'] / len(chord_notes),
                                start=current_time + converted_start + (i * 0.2),
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
                    else:  # groove
                        # Groove-based pattern
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
        
        logger.info(f"Generated {len(pattern)} bass notes")
        return pattern 