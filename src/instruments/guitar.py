"""Guitar instrument implementation."""

from typing import List, Any, Tuple, Dict
from .base import BaseInstrument
from ..core.song_parser import SongData, Section
from ..patterns.pattern_manager import PatternManager
from ..patterns.variation_manager import VariationManager, VariationType

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
        self._last_chord = None
        self._last_time = 0.0
        self._pattern_manager = PatternManager()
        self._variation_manager = VariationManager()
        self._song_length = 0.0
        self._last_pattern_time = 0.0
        self._min_pattern_interval = 4.0  # Minimum beats between pattern applications

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
    
    def _verify_song_characteristics(self, song_data: SongData) -> None:
        """Verify that the song's key and tempo are valid and supported.
        
        Args:
            song_data: Song data containing the song's characteristics
            
        Raises:
            ValueError: If key or tempo is invalid or unsupported
        """
        # Verify key
        if not song_data.key:
            raise ValueError("Song key is missing")
        
        key_parts = song_data.key.split()
        if len(key_parts) < 2:
            raise ValueError(f"Invalid key format: {song_data.key}. Expected format: 'note mode' (e.g., 'E minor')")
        
        key_note = key_parts[0].upper()
        key_mode = key_parts[1].lower()
        
        valid_notes = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        valid_modes = ['major', 'minor']
        
        if key_note[0] not in valid_notes:
            raise ValueError(f"Invalid key note: {key_note}. Must be one of {valid_notes}")
        
        if key_mode not in valid_modes:
            raise ValueError(f"Invalid key mode: {key_mode}. Must be one of {valid_modes}")
        
        # Verify tempo
        if not song_data.tempo:
            raise ValueError("Song tempo is missing")
        
        if not isinstance(song_data.tempo, (int, float)) or song_data.tempo <= 0:
            raise ValueError(f"Invalid tempo: {song_data.tempo}. Must be a positive number")
        
        if song_data.tempo < 40 or song_data.tempo > 208:
            raise ValueError(f"Tempo {song_data.tempo} BPM is outside supported range (40-208 BPM)")

    def _get_section_for_time(self, time: float, sections: List[Section]) -> Section:
        """Get the section that contains the given time.
        
        Args:
            time: Time in beats
            sections: List of sections
            
        Returns:
            Section containing the time, or None if no section contains it
        """
        for section in sections:
            if section.start_time <= time <= section.end_time:
                return section
        return None

    def _get_section_mood(self, section: Section) -> str:
        """Extract mood from section comments or return default."""
        if not section or not section.comments:
            return "neutral"
        
        comments = section.comments.lower()
        if "energetic" in comments or "upbeat" in comments:
            return "energetic"
        elif "calm" in comments or "peaceful" in comments:
            return "calm"
        elif "sad" in comments or "melancholic" in comments:
            return "sad"
        elif "happy" in comments or "joyful" in comments:
            return "happy"
        return "neutral"

    def generate_pattern(self, song_data: SongData, chord: str = None, style: str = None) -> List[Tuple[int, float, float, int]]:
        """Generate guitar pattern that's compatible with the sample song.
        
        Args:
            song_data: Song data containing the sample song's structure
            chord: Optional chord to use as base (defaults to key root)
            style: Optional style/genre of the song
            
        Returns:
            List of (note, time, duration, velocity) tuples
            
        Raises:
            ValueError: If song characteristics are invalid
        """
        # Verify song characteristics before generating pattern
        self._verify_song_characteristics(song_data)
        
        events = []
        import random
        import time
        
        # Set random seed based on current time to ensure different patterns each time
        random.seed(int(time.time() * 1000))  # Use milliseconds for more variation
        
        # Calculate total song length from sections
        total_song_length = max(section.end_time for section in song_data.sections)
        
        # Analyze the sample song's structure
        key_root = self._parse_key_root(song_data.key.split()[0])
        is_minor = "minor" in song_data.key.lower()
        
        # Use provided chord or default to key root
        if chord:
            key_root = self._parse_key_root(chord)
        
        # Define scale degrees for the key
        scale_degrees = {
            'major': [0, 2, 4, 5, 7, 9, 11],  # C major scale degrees
            'minor': [0, 2, 3, 5, 7, 8, 10]   # C minor scale degrees
        }
        scale = scale_degrees['minor' if is_minor else 'major']
        
        # Store tempo for rhythm adjustments
        tempo = song_data.tempo
        
        # Validate and adjust pattern durations based on tempo
        def adjust_duration(duration: float) -> float:
            """Adjust note duration based on tempo."""
            if tempo <= 60:
                return duration * 1.2  # Slower tempo, longer notes
            elif tempo >= 120:
                return duration * 0.8  # Faster tempo, shorter notes
            return duration
        
        # Validate note range
        min_note, max_note = self.get_playable_range()
        def validate_note(note: int) -> int:
            """Ensure note is within playable range."""
            while note < min_note:
                note += 12
            while note > max_note:
                note -= 12
            return note
        
        # Define possible patterns for each section type with more variations
        intro_patterns = [
            # Pattern 1: Arpeggiated chords
            lambda t, i: [(key_root + scale[i % len(scale)], t, 1.0, 45)] if i % 2 == 0 else [],
            # Pattern 2: Fingerpicked
            lambda t, i: [(key_root, t, 0.5, 40), (key_root + 4, t + 0.25, 0.5, 35), (key_root + 7, t + 0.5, 0.5, 35)] if i % 2 == 0 else [],
            # Pattern 3: Single note with echo
            lambda t, i: [(key_root, t, 1.0, 45), (key_root, t + 0.5, 0.5, 35)] if i % 2 == 0 else [],
            # Pattern 4: Alternating intervals
            lambda t, i: [(key_root, t, 0.5, 45), (key_root + 4, t + 0.25, 0.5, 40)] if i % 2 == 0 else [],
            # Pattern 5: Harmonic notes
            lambda t, i: [(key_root, t, 1.0, 40), (key_root + 12, t, 1.0, 35)] if i % 4 == 0 else []
        ]
        
        verse_patterns = [
            # Pattern 1: Strummed chords
            lambda t, i: [(key_root, t, 0.5, 60), (key_root + 4, t, 0.5, 55), (key_root + 7, t, 0.5, 55)] if i % 2 == 0 else [],
            # Pattern 2: Palm muted
            lambda t, i: [(key_root, t, 0.25, 50), (key_root + 4, t + 0.25, 0.25, 45), (key_root + 7, t + 0.5, 0.25, 45)] if i % 2 == 0 else [],
            # Pattern 3: Power chords
            lambda t, i: [(key_root, t, 0.5, 55), (key_root + 7, t, 0.5, 50)] if i % 2 == 0 else [],
            # Pattern 4: Alternating bass
            lambda t, i: [(key_root, t, 0.5, 55), (key_root + 4, t + 0.25, 0.5, 50), (key_root + 7, t + 0.5, 0.5, 50)] if i % 2 == 0 else [],
            # Pattern 5: Syncopated strums
            lambda t, i: [(key_root, t, 0.25, 60), (key_root + 4, t + 0.25, 0.25, 55), (key_root + 7, t + 0.5, 0.25, 55)] if i % 2 == 0 else []
        ]
        
        chorus_patterns = [
            # Pattern 1: Full strums
            lambda t, i: [(key_root, t, 0.5, 75), (key_root + 4, t, 0.5, 70), (key_root + 7, t, 0.5, 70), (key_root + 12, t, 0.5, 65)] if i % 2 == 0 else [],
            # Pattern 2: Power chords
            lambda t, i: [(key_root, t, 0.5, 80), (key_root + 7, t, 0.5, 75), (key_root + 12, t, 0.5, 70)] if i % 2 == 0 else [],
            # Pattern 3: Octave chords
            lambda t, i: [(key_root, t, 0.5, 75), (key_root + 12, t, 0.5, 70), (key_root + 7, t + 0.25, 0.5, 65)] if i % 2 == 0 else [],
            # Pattern 4: Barre chords
            lambda t, i: [(key_root, t, 0.5, 80), (key_root + 4, t, 0.5, 75), (key_root + 7, t, 0.5, 75), (key_root + 11, t, 0.5, 70)] if i % 2 == 0 else [],
            # Pattern 5: Staccato strums
            lambda t, i: [(key_root, t, 0.25, 80), (key_root + 4, t, 0.25, 75), (key_root + 7, t, 0.25, 75)] if i % 2 == 0 else []
        ]
        
        bridge_patterns = [
            # Pattern 1: Contrasting chords
            lambda t, i: [(key_root + 5 if i % 8 == 0 else key_root + 7, t, 1.0, 65), (key_root + 9 if i % 8 == 0 else key_root + 11, t, 1.0, 60)] if i % 4 == 0 else [],
            # Pattern 2: Chromatic movement
            lambda t, i: [(key_root + scale[i % len(scale)], t, 0.5, 65)] if i % 2 == 0 else [],
            # Pattern 3: Suspended chords
            lambda t, i: [(key_root + 5, t, 0.5, 65), (key_root + 9, t, 0.5, 60), (key_root + 11, t, 0.5, 60)] if i % 2 == 0 else [],
            # Pattern 4: Alternating inversions
            lambda t, i: [(key_root + 7, t, 0.5, 65), (key_root + 4, t + 0.25, 0.5, 60), (key_root, t + 0.5, 0.5, 55)] if i % 4 == 0 else [],
            # Pattern 5: Dissonant intervals
            lambda t, i: [(key_root + 1, t, 0.5, 65), (key_root + 6, t + 0.25, 0.5, 60)] if i % 2 == 0 else []
        ]
        
        outro_patterns = [
            # Pattern 1: Fading strums
            lambda t, i: [(key_root, t, 1.0, max(30, 70 - (i // 4) * 10)), (key_root + 7, t, 1.0, max(25, 65 - (i // 4) * 10))] if i % 4 == 0 else [],
            # Pattern 2: Dwindling arpeggio
            lambda t, i: [(key_root + scale[i % len(scale)], t, 0.5, max(30, 70 - (i // 2) * 5))] if i % 2 == 0 else [],
            # Pattern 3: Simple resolution
            lambda t, i: [(key_root, t, 1.0, max(30, 70 - (i // 4) * 10))] if i % 4 == 0 else [],
            # Pattern 4: Echoing notes
            lambda t, i: [(key_root, t, 0.5, max(30, 70 - (i // 2) * 5)), (key_root, t + 0.25, 0.25, max(20, 60 - (i // 2) * 5))] if i % 2 == 0 else [],
            # Pattern 5: Fading intervals
            lambda t, i: [(key_root, t, 0.5, max(30, 70 - (i // 2) * 5)), (key_root + 4, t + 0.25, 0.5, max(25, 65 - (i // 2) * 5))] if i % 2 == 0 else []
        ]
        
        # Generate patterns for each section
        for section in song_data.sections:
            section_start = section.start_time
            section_end = section.end_time
            section_duration = section_end - section_start
            
            # Analyze section type and mood
            section_type = section.name.lower()
            mood = self._get_section_mood(section)
            
            # Select random pattern based on section type
            if "intro" in section_type:
                pattern = random.choice(intro_patterns)
            elif "verse" in section_type:
                pattern = random.choice(verse_patterns)
            elif "chorus" in section_type:
                pattern = random.choice(chorus_patterns)
            elif "bridge" in section_type:
                pattern = random.choice(bridge_patterns)
            elif "outro" in section_type:
                pattern = random.choice(outro_patterns)
            else:
                pattern = random.choice(verse_patterns)  # Default to verse pattern
            
            # Apply the selected pattern with length and range validation
            for i in range(int(section_duration)):
                time = section_start + i
                new_events = pattern(time, i)
                
                # Validate and adjust each event
                for note, t, dur, vel in new_events:
                    # Validate note range
                    validated_note = validate_note(note)
                    
                    # Adjust duration based on tempo
                    adjusted_duration = adjust_duration(dur)
                    
                    # Ensure event doesn't extend beyond section
                    if t + adjusted_duration > section_end:
                        adjusted_duration = section_end - t
                    
                    # Only add if duration is positive
                    if adjusted_duration > 0:
                        events.append((validated_note, t, adjusted_duration, vel))
        
        # Sort events by time
        events = sorted(events, key=lambda x: x[1])
        
        # Validate total pattern length
        if events:
            last_event_time = events[-1][1] + events[-1][2]  # last start time + duration
            if last_event_time < total_song_length:
                # Add sustaining notes to fill the gap
                gap_start = last_event_time
                while gap_start < total_song_length:
                    # Add a sustaining note using the key root
                    duration = min(2.0, total_song_length - gap_start)
                    events.append((key_root, gap_start, duration, 45))  # Soft velocity for fill
                    gap_start += duration
            elif last_event_time > total_song_length:
                # Trim events that extend beyond song length
                events = [(n, t, min(d, total_song_length - t), v) for n, t, d, v in events if t < total_song_length]
        
        return events 