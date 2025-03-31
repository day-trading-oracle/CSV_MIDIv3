"""Drums instrument implementation."""

from typing import List, Any, Tuple, Dict
from .base import BaseInstrument
from ..core.song_parser import SongData

class Drums(BaseInstrument):
    """Drums instrument class."""
    
    # MIDI note numbers for drum sounds
    DRUM_NOTES = {
        'kick': 36,    # C1
        'snare': 38,   # D1
        'hihat': 42,   # F#1
        'crash': 49,   # C#2
        'ride': 51,    # D#2
        'toms': [45, 47, 50]  # A1, B1, D2
    }
    
    # Standard patterns by style
    PATTERNS = {
        'classical': {
            'rhythm': [(0, 1.0), (2, 1.0)],  # Half notes
            'velocity': 80
        },
        'jazz': {
            'rhythm': [(0, 0.5), (1, 0.5), (2, 0.5), (3, 0.5)],  # Swing pattern
            'velocity': 90
        },
        'pop': {
            'rhythm': [(0, 0.5), (2, 0.5), (3, 0.5)],  # Common pop pattern
            'velocity': 85
        },
        'rock': {
            'rhythm': [(0, 0.5), (1.5, 0.5), (2, 0.5), (3, 0.5)],  # Rock pattern
            'velocity': 95
        }
    }
    
    def __init__(self, midi_channel: int = 9, velocity: int = 100):
        """Initialize the drums."""
        super().__init__("Drums", midi_channel, velocity)
    
    def get_playable_range(self) -> tuple[int, int]:
        """Get the playable MIDI note range for drums."""
        return (35, 81)  # B0 to A5
    
    def _create_note_event(self, note: int, time: float, duration: float, velocity: int = None) -> Tuple[int, float, float]:
        """Create a note event tuple."""
        return (note, time, duration)
    
    def _parse_note(self, note_str: str) -> List[int]:
        """Parse a note string into MIDI note numbers."""
        # Map note names to drum sounds
        note_map = {
            'kick': self.DRUM_NOTES['kick'],
            'snare': self.DRUM_NOTES['snare'],
            'hihat': self.DRUM_NOTES['hihat'],
            'crash': self.DRUM_NOTES['crash'],
            'ride': self.DRUM_NOTES['ride'],
            'toms': self.DRUM_NOTES['toms']
        }
        
        # Default to hi-hat if note not recognized
        return [note_map.get(note_str.lower(), self.DRUM_NOTES['hihat'])]
    
    def _dynamic_to_velocity(self, dynamic: str) -> int:
        """Convert dynamic marking to velocity."""
        dynamics = {
            'pp': 20,
            'p': 40,
            'mp': 60,
            'mf': 80,
            'f': 100,
            'ff': 120
        }
        return dynamics.get(dynamic.lower(), 80)
    
    def _duration_to_beats(self, duration: str) -> float:
        """Convert duration string to beats."""
        durations = {
            'whole': 4.0,
            'half': 2.0,
            'quarter': 1.0,
            'eighth': 0.5,
            'sixteenth': 0.25
        }
        return durations.get(duration.lower(), 1.0)
    
    def generate_pattern(self, chord: str, style: str = "classical", song_data: SongData = None) -> List[dict]:
        """Generate a drum pattern based on the song data.
        
        Args:
            chord: Current chord (not used for drums)
            style: Musical style/genre
            song_data: Song data containing notes and timing
            
        Returns:
            List of MIDI note events
        """
        try:
            pattern = []
            
            # Get style pattern for default rhythm if no song data provided
            style_pattern = self.PATTERNS.get(style.lower(), self.PATTERNS['classical'])
            base_velocity = style_pattern.get('velocity', 80)
            
            if not song_data or not song_data.notes:
                # Use default pattern if no notes provided
                for beat, duration in style_pattern['rhythm']:
                    # Add basic drum pattern
                    pattern.append(self._create_note_event(self.DRUM_NOTES['kick'], beat, duration, base_velocity))
                    pattern.append(self._create_note_event(self.DRUM_NOTES['hihat'], beat, duration, base_velocity))
                    if beat % 2 == 0:  # Add snare on even beats
                        pattern.append(self._create_note_event(self.DRUM_NOTES['snare'], beat, duration, base_velocity))
            else:
                # Use song data notes
                for note_info in song_data.notes:
                    try:
                        # Get timing information
                        time = note_info['time']
                        duration = self._duration_to_beats(note_info['duration'])
                        dynamic = note_info['dynamic']
                        velocity = self._dynamic_to_velocity(dynamic)
                        
                        # Get drum sound
                        note_str = note_info['note']
                        notes = self._parse_note(note_str)
                        for note in notes:
                            pattern.append(self._create_note_event(
                                note,
                                time,
                                duration,
                                velocity
                            ))
                    except Exception as e:
                        print(f"Warning: Skipping invalid drum event: {note_info}. Error: {str(e)}")
                        continue
            
            return pattern
            
        except Exception as e:
            print(f"Error generating drum pattern: {str(e)}")
            # Return a simple pattern as fallback
            return [
                (self.DRUM_NOTES['kick'], 0, 1.0, 80),
                (self.DRUM_NOTES['hihat'], 0, 1.0, 80)
            ] 