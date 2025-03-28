"""
Bass instrument implementation with bass-specific music theory and patterns.
"""

from typing import Dict, List, Optional, Tuple
from .base import BaseInstrument, NoteData
from ..utils import normalize_velocity

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
    
    def get_playable_range(self) -> Tuple[int, int]:
        """Get the playable range for the bass instrument."""
        return (24, 55)  # C1 to G3
    
    def _create_walking_pattern(self, chord: List[int], duration: float) -> List[NoteData]:
        """Create a walking bass pattern."""
        pattern = []
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
    
    def generate_pattern(self, song_data: Dict, style: Optional[str] = None, genre: Optional[str] = None) -> List[Dict]:
        """Generate a bass pattern based on the song data and style.
        
        Args:
            song_data: Dictionary containing song information
            style: Optional style specification (walking, rock, funk, jazz, pop)
            genre: Optional genre specification (classical, jazz, rock, funk, pop)
        
        Returns:
            List of note events for the bass track
        """
        if not style:
            style = 'walking'  # Default to walking bass
        
        if not genre:
            genre = 'classical'  # Default to classical
        
        # Get the appropriate chord progression
        progression = self.chord_progressions.get(genre, self.chord_progressions['classical'])
        
        # Get the pattern generator function
        pattern_func = self.patterns.get(style, self._create_walking_pattern)
        
        # Generate notes for each measure
        notes = []
        current_time = 0
        
        for measure in song_data['measures']:
            # Get the chord for this measure (simplified)
            chord = progression[0]  # For now, just use the first chord
            
            # Generate the pattern for this measure
            measure_notes = pattern_func(chord, 4.0)  # Assuming 4/4 time
            
            # Add the notes to the output with proper timing
            for note in measure_notes:
                notes.append({
                    'pitch': note.pitch,
                    'duration': note.duration,
                    'start': current_time + note.start,
                    'velocity': note.velocity
                })
            
            current_time += 4.0  # Move to next measure
        
        # Ensure we have at least one note
        if not notes:
            # Create a simple root note pattern as fallback
            notes.append({
                'pitch': 36,  # C2
                'duration': 1.0,
                'start': 0,
                'velocity': 80
            })
        
        return notes 