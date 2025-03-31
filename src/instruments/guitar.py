"""Guitar instrument implementation."""

from typing import List, Any, Tuple, Dict
from .base import BaseInstrument
from ..core.song_parser import SongData

class Guitar(BaseInstrument):
    """Guitar instrument class."""
    
    # MIDI note numbers for basic guitar chords (C major scale)
    CHORD_NOTES = {
        'C': [48, 52, 55, 60, 64, 67],    # C3, E3, G3, C4, E4, G4
        'Dm': [50, 53, 57, 62, 65, 69],   # D3, F3, A3, D4, F4, A4
        'Em': [52, 55, 59, 64, 67, 71],   # E3, G3, B3, E4, G4, B4
        'F': [53, 57, 60, 65, 69, 72],    # F3, A3, C4, F4, A4, C5
        'G': [55, 59, 62, 67, 71, 74],    # G3, B3, D4, G4, B4, D5
        'Am': [57, 60, 64, 69, 72, 76],   # A3, C4, E4, A4, C5, E5
        'Bdim': [59, 62, 65, 71, 74, 77], # B3, D4, F4, B4, D5, F5
    }
    
    # Standard patterns by style
    PATTERNS = {
        'classical': {
            'rhythm': [(0, 1.0), (2, 1.0)],  # Half notes
            'velocity': 80
        },
        'jazz': {
            'rhythm': [(0, 0.5), (1, 0.5), (2, 0.5), (3, 0.5)],  # Quarter notes
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
    
    def __init__(self, midi_channel: int = 1, velocity: int = 100):
        """Initialize the guitar.
        
        Args:
            midi_channel: MIDI channel number (0-15)
            velocity: Default note velocity (0-127)
        """
        super().__init__("Guitar", midi_channel, velocity)
    
    def get_playable_range(self) -> tuple[int, int]:
        """Get the playable MIDI note range for guitar.
        
        Returns:
            Tuple of (lowest_note, highest_note) in MIDI note numbers
        """
        return (40, 88)  # E2 to E6
    
    def _create_note_event(self, note: int, time: float, duration: float, velocity: int = None) -> Tuple[int, float, float]:
        """Create a note event tuple.
        
        Args:
            note: MIDI note number
            time: Start time in beats
            duration: Duration in beats
            velocity: Note velocity (0-127)
            
        Returns:
            Tuple of (note, time, duration)
        """
        return (note, time, duration)
    
    def _parse_note(self, note_str: str) -> List[int]:
        """Parse a note string into MIDI note numbers.
        
        Args:
            note_str: Note string (e.g., "C4", "Fs4", "[E3,G3,B3]")
            
        Returns:
            List of MIDI note numbers
        """
        # Handle chord notation
        if note_str.startswith('[') and note_str.endswith(']'):
            chord_notes = note_str[1:-1].split(',')
            return [self._parse_single_note(note.strip()) for note in chord_notes]
        
        # Handle single note
        return [self._parse_single_note(note_str)]
    
    def _parse_single_note(self, note_str: str) -> int:
        """Parse a single note string into MIDI note number.
        
        Args:
            note_str: Note string (e.g., "C4", "Fs4")
            
        Returns:
            MIDI note number
        """
        # Handle sharp notes
        if 's' in note_str:
            note_name = note_str.split('s')[0].upper()
            octave = int(note_str[-1])
            base_note = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}[note_name]
            return base_note + 1 + (octave + 1) * 12  # Add 1 for sharp
        
        # Handle regular notes
        note_name = note_str[0].upper()
        octave = int(note_str[-1])
        base_note = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}[note_name]
        return base_note + (octave + 1) * 12
    
    def _note_to_midi(self, note: str) -> int:
        """Convert note name to MIDI note number.
        
        Args:
            note: Note name (e.g., "E3")
            
        Returns:
            MIDI note number
        """
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        note_name = note[:-1]
        octave = int(note[-1])
        note_index = notes.index(note_name)
        return 12 * (octave + 1) + note_index
    
    def _dynamic_to_velocity(self, dynamic: str) -> int:
        """Convert dynamic marking to velocity.
        
        Args:
            dynamic: Dynamic marking (pp, p, mp, mf, f, ff)
            
        Returns:
            MIDI velocity (0-127)
        """
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
        """Convert duration string to beats.
        
        Args:
            duration: Duration string (whole, half, quarter, eighth, sixteenth)
            
        Returns:
            Duration in beats
        """
        durations = {
            'whole': 4.0,
            'half': 2.0,
            'quarter': 1.0,
            'eighth': 0.5,
            'sixteenth': 0.25
        }
        return durations.get(duration.lower(), 1.0)
    
    def generate_pattern(self, chord: str, style: str = "classical", song_data: SongData = None) -> List[dict]:
        """Generate a guitar pattern based on the song data.
        
        Args:
            chord: Current chord (e.g., "C", "Am", "F#m")
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
                chord_notes = self.CHORD_NOTES.get(chord, self.CHORD_NOTES['C'])
                for beat, duration in style_pattern['rhythm']:
                    for note in chord_notes:
                        pattern.append(self._create_note_event(note, beat, duration, base_velocity))
            else:
                # Use song data notes
                for note_info in song_data.notes:
                    try:
                        # Get timing information
                        time = note_info['time']
                        duration = self._duration_to_beats(note_info['duration'])
                        dynamic = note_info['dynamic']
                        velocity = self._dynamic_to_velocity(dynamic)
                        
                        # Get note or chord
                        note_str = note_info['note']
                        notes = self._parse_note(note_str)
                        
                        if len(notes) > 1:  # It's a chord
                            # For guitar, we strum the chord
                            for i, note in enumerate(notes):
                                # Stagger the notes slightly for a strum effect
                                strum_delay = i * 0.05  # 50ms between each note
                                pattern.append(self._create_note_event(
                                    note,
                                    time + strum_delay,
                                    duration - strum_delay,
                                    velocity
                                ))
                        else:  # Single note
                            pattern.append(self._create_note_event(
                                notes[0],
                                time,
                                duration,
                                velocity
                            ))
                    except Exception as e:
                        print(f"Warning: Skipping invalid note event: {note_info}. Error: {str(e)}")
                        continue
            
            return pattern
            
        except Exception as e:
            print(f"Error generating guitar pattern: {str(e)}")
            # Return a simple pattern as fallback
            return [(self.CHORD_NOTES['C'][0], 0, 1.0, 80)] 