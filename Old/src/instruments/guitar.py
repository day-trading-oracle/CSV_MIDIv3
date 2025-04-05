"""Guitar instrument implementation."""

from typing import List, Any, Tuple, Dict
from .base import BaseInstrument
from ..core.song_parser import SongData, Section
from ..patterns.pattern_manager import PatternManager
from ..patterns.variation_manager import VariationManager, VariationType

class Guitar(BaseInstrument):
    """Guitar instrument class."""
    
    # Extended MIDI note numbers for guitar chords with more voicings
    CHORD_NOTES = {
        'C': {
            'basic': [48, 52, 55, 60, 64, 67],    # C3, E3, G3, C4, E4, G4
            'power': [48, 55, 60],                # C3, G3, C4
            'jazz': [48, 52, 55, 58, 64],         # C3, E3, G3, Bb3, E4
            'sus4': [48, 53, 55],                 # C3, F3, G3
            'add9': [48, 52, 55, 62]              # C3, E3, G3, D4
        },
        'Dm': {
            'basic': [50, 53, 57, 62, 65, 69],    # D3, F3, A3, D4, F4, A4
            'power': [50, 57, 62],                # D3, A3, D4
            'jazz': [50, 53, 57, 60, 65],         # D3, F3, A3, C4, F4
            'sus4': [50, 55, 57],                 # D3, G3, A3
            'add9': [50, 53, 57, 64]              # D3, F3, A3, E4
        }
    }
    
    # Strumming patterns by style
    STRUM_PATTERNS = {
        'rock': [
            (1.0, 'down', 0.8),   # Down strum on beat 1
            (1.5, 'up', 0.6),     # Up strum on "and" of 1
            (2.0, 'down', 0.7),   # Down strum on beat 2
            (2.5, 'up', 0.6),     # Up strum on "and" of 2
            (3.0, 'down', 0.7),   # Down strum on beat 3
            (3.5, 'up', 0.6),     # Up strum on "and" of 3
            (4.0, 'down', 0.7),   # Down strum on beat 4
            (4.5, 'up', 0.6)      # Up strum on "and" of 4
        ],
        'pop': [
            (1.0, 'down', 0.7),   # Down strum on beat 1
            (2.0, 'down', 0.6),   # Down strum on beat 2
            (2.5, 'up', 0.5),     # Up strum on "and" of 2
            (3.0, 'down', 0.6),   # Down strum on beat 3
            (4.0, 'down', 0.6),   # Down strum on beat 4
            (4.5, 'up', 0.5)      # Up strum on "and" of 4
        ],
        'jazz': [
            (1.0, 'down', 0.6),   # Light down strum on beat 1
            (2.0, 'up', 0.5),     # Light up strum on beat 2
            (3.0, 'down', 0.6),   # Light down strum on beat 3
            (4.0, 'up', 0.5)      # Light up strum on beat 4
        ]
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

    def _parse_key_root(self, key_str: str) -> int:
        """Parse the root note of a key and return its MIDI note number.
        
        Args:
            key_str: Key string (e.g., "C", "F#", "Bb")
            
        Returns:
            MIDI note number for the root note (middle C = 60)
            
        Raises:
            ValueError: If key string is invalid
        """
        # Remove any accidentals (sharp/flat)
        key_str = key_str.strip().upper()
        root = key_str[0]
        
        # Define MIDI note numbers for root notes (using middle C = 60)
        root_notes = {
            'C': 60,  # Middle C
            'D': 62,
            'E': 64,
            'F': 65,
            'G': 67,
            'A': 69,
            'B': 71
        }
        
        if root not in root_notes:
            raise ValueError(f"Invalid key root: {root}. Must be one of {list(root_notes.keys())}")
        
        # Handle sharp/flat modifiers
        if len(key_str) > 1:
            if key_str[1] == '#':
                return root_notes[root] + 1
            elif key_str[1] == 'B':
                return root_notes[root] - 1
        
        return root_notes[root]

    def get_playable_range(self) -> tuple[int, int]:
        """Get the playable MIDI note range for guitar.
        
        Returns:
            Tuple of (lowest_note, highest_note) in MIDI note numbers
        """
        return (40, 84)  # E2 to C6
    
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

    def _get_chord_voicing(self, root_note: int, chord_type: str, style: str) -> List[int]:
        """Get appropriate chord voicing based on style and section.
        
        Args:
            root_note: MIDI note number of the root note
            chord_type: Type of chord (major, minor, etc.)
            style: Musical style/genre
            
        Returns:
            List of MIDI note numbers for the chord voicing
        """
        base_voicing = [root_note, root_note + 4, root_note + 7]  # Basic triad
        
        if style == 'rock':
            # Power chords for rock
            return [root_note, root_note + 7, root_note + 12]
        elif style == 'jazz':
            # Extended chords for jazz
            return base_voicing + [root_note + 10, root_note + 14]
        elif style == 'pop':
            # Open voicings for pop
            return [root_note, root_note + 7, root_note + 12, root_note + 16]
        else:
            return base_voicing
            
    def _apply_strum_pattern(self, root_note: int, chord_voicing: List[int], 
                            style: str, start_time: float) -> List[Tuple[int, float, float, int]]:
        """Apply a strumming pattern to a chord voicing.
        
        Args:
            root_note: MIDI note number of the root note
            chord_voicing: List of MIDI note numbers for the chord
            style: Musical style/genre
            start_time: Start time for the pattern
            
        Returns:
            List of (note, time, duration, velocity) tuples
        """
        events = []
        pattern = self.STRUM_PATTERNS.get(style, self.STRUM_PATTERNS['rock'])
        
        for beat, direction, velocity_mult in pattern:
            time = start_time + (beat - 1.0)  # Convert 1-based beat to time offset
            notes = chord_voicing if direction == 'down' else reversed(chord_voicing)
            delay = 0.0
            
            for note in notes:
                # Add slight delay between notes for more realistic strumming
                events.append((note, time + delay, 0.5, int(100 * velocity_mult)))
                delay += 0.02
                
        return events
        
    def _create_melodic_fill(self, root_note: int, scale: List[int], style: str) -> List[Tuple[int, float, float, int]]:
        """Create a melodic fill based on the current chord and style.
        
        Args:
            root_note: MIDI note number of the root note
            scale: List of scale degrees
            style: Musical style/genre
            
        Returns:
            List of (note, time, duration, velocity) tuples for the fill
        """
        import random
        
        fill_notes = []
        if style == 'rock':
            # Create power chord based fills
            for i in range(2):
                note = root_note + random.choice([0, 7, 12])
                fill_notes.append((note, i * 0.5, 0.5, random.randint(70, 85)))
        elif style == 'jazz':
            # Create chromatic approach note fills
            for i in range(4):
                note = root_note + random.choice(scale)
                fill_notes.append((note, i * 0.25, 0.25, random.randint(60, 75)))
        elif style == 'pop':
            # Create simple melodic hooks
            for i in range(2):
                note = root_note + random.choice(scale[:5])
                fill_notes.append((note, i * 0.5, 0.5, 65))
                
        return fill_notes

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
        self._verify_song_characteristics(song_data)
        
        events = []
        import random
        import time
        
        random.seed(int(time.time() * 1000))
        
        # Analyze song structure
        key_root = self._parse_key_root(song_data.key.split()[0])
        is_minor = "minor" in song_data.key.lower()
        
        if chord:
            key_root = self._parse_key_root(chord)
        
        scale_degrees = {
            'major': [0, 2, 4, 5, 7, 9, 11],
            'minor': [0, 2, 3, 5, 7, 8, 10]
        }
        scale = scale_degrees['minor' if is_minor else 'major']
        
        tempo = song_data.tempo
        
        def adjust_duration(duration: float) -> float:
            """Adjust note duration based on tempo and style."""
            base_adjustment = 1.0
            if tempo <= 60:
                base_adjustment = 1.2
            elif tempo >= 120:
                base_adjustment = 0.8
                
            if style == 'jazz':
                base_adjustment *= 0.8  # Shorter, snappier notes for jazz
            elif style == 'rock':
                base_adjustment *= 0.9  # Slightly shorter for rock
                
            return duration * base_adjustment
        
        min_note, max_note = self.get_playable_range()
        def validate_note(note: int) -> int:
            while note < min_note:
                note += 12
            while note > max_note:
                note -= 12
            return note
            
        # Enhanced patterns for different sections
        intro_patterns = [
            # Clean arpeggios
            lambda t, i: [(validate_note(key_root + n), t + (j * 0.25), 0.25, 45 + (j * 5)) 
                         for j, n in enumerate([0, 4, 7, 12]) if i % 2 == 0],
            # Ambient chords
            lambda t, i: self._apply_strum_pattern(
                key_root,
                self._get_chord_voicing(key_root, 'major', style or 'rock'),
                style or 'rock',
                t
            ),
            # Melodic fills
            lambda t, i: self._create_melodic_fill(key_root, scale, style or 'rock') if i % 4 == 0 else []
        ]
        
        verse_patterns = [
            # Rhythmic strumming
            lambda t, i: self._apply_strum_pattern(
                key_root,
                self._get_chord_voicing(key_root, 'major', style or 'rock'),
                style or 'rock',
                t
            ),
            # Palm-muted power chords
            lambda t, i: [(validate_note(key_root), t, 0.5, 65)] + 
                        [(validate_note(key_root + n), t + 0.5, 0.5, 55) 
                         for n in [7, 12]] if i % 2 == 0 else [],
            # Clean single notes with chord backing
            lambda t, i: [(validate_note(key_root + scale[i % len(scale)]), t, 0.25, 65)] +
                        [(validate_note(key_root + n), t, 1.0, 45) 
                         for n in [0, 7]] if i % 2 == 0 else []
        ]
        
        chorus_patterns = [
            # Full power chords
            lambda t, i: self._apply_strum_pattern(
                key_root,
                self._get_chord_voicing(key_root, 'major', 'rock'),
                'rock',
                t
            ),
            # Rhythmic chord stabs
            lambda t, i: [(validate_note(key_root + n), t + (j * 0.25), 0.25, 70) 
                         for j, n in enumerate([0, 7, 12])] if i % 2 == 0 else [],
            # Sustained chords with fills
            lambda t, i: [(validate_note(key_root + n), t, 1.0, 70) 
                         for n in self._get_chord_voicing(key_root, 'major', style or 'rock')] +
                        self._create_melodic_fill(key_root + 12, scale, style or 'rock')
        ]
        
        bridge_patterns = [
            # Complex voicings
            lambda t, i: self._apply_strum_pattern(
                key_root,
                self._get_chord_voicing(key_root, 'major', 'jazz'),
                'jazz',
                t
            ),
            # Alternating voicings
            lambda t, i: [(validate_note(key_root + n), t, 0.5, 65) 
                         for n in self._get_chord_voicing(key_root, 'major', style or 'rock')] +
                        [(validate_note(key_root + n + 2), t + 0.5, 0.5, 60) 
                         for n in self._get_chord_voicing(key_root, 'major', style or 'rock')],
            # Lead fills
            lambda t, i: [(validate_note(key_root), t, 1.0, 60)] +
                        self._create_melodic_fill(key_root + 12, scale, style or 'rock')
        ]
        
        outro_patterns = [
            # Fading strums
            lambda t, i: self._apply_strum_pattern(
                key_root,
                self._get_chord_voicing(key_root, 'major', style or 'rock'),
                style or 'rock',
                t
            ),
            # Final power chords
            lambda t, i: [(validate_note(key_root + n), t, 2.0, max(30, 50 - (i // 4) * 5)) 
                         for n in [0, 7, 12]],
            # Gentle resolution
            lambda t, i: [(validate_note(key_root + n), t, 2.0, max(30, 50 - (i // 4) * 5)) 
                         for n in self._get_chord_voicing(key_root, 'major', 'rock')]
        ]
        
        # Process each section
        for section in song_data.sections:
            current_time = section.start_time
            pattern_index = 0
            
            # Select patterns based on section type
            if section.type == "intro":
                patterns = intro_patterns
            elif section.type == "verse":
                patterns = verse_patterns
            elif section.type == "chorus":
                patterns = chorus_patterns
            elif section.type == "bridge":
                patterns = bridge_patterns
            elif section.type == "outro":
                patterns = outro_patterns
            else:
                patterns = verse_patterns  # Default to verse patterns
                
            # Generate events for this section
            while current_time < section.end_time:
                # Select and apply pattern
                pattern = patterns[pattern_index % len(patterns)]
                new_events = pattern(current_time, pattern_index)
                
                # Add fills at pattern transitions
                if pattern_index % 4 == 3:  # Every fourth pattern
                    fill_events = self._create_melodic_fill(key_root + 12, scale, style or 'rock')
                    new_events.extend([(note, t + current_time, dur, vel) for note, t, dur, vel in fill_events])
                
                # Add events with adjusted durations
                for note, time, duration, velocity in new_events:
                    adjusted_duration = adjust_duration(duration)
                    if time + adjusted_duration <= section.end_time:
                        events.append((note, time, adjusted_duration, velocity))
                
                current_time += 1.0  # Move to next beat
                pattern_index += 1
        
        return events 