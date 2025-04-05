"""Bass instrument implementation."""

from typing import List, Any, Tuple, Dict
from .base import BaseInstrument
from ..core.song_parser import SongData, Section
from ..patterns.pattern_manager import PatternManager
from ..patterns.variation_manager import VariationManager, VariationType

class Bass(BaseInstrument):
    """Bass instrument class."""
    
    # Extended MIDI note numbers for bass patterns
    BASS_PATTERNS = {
        'walking': {
            'major': [0, 4, 7, 9],      # Root, third, fifth, sixth
            'minor': [0, 3, 7, 8]       # Root, minor third, fifth, minor sixth
        },
        'groove': {
            'major': [0, 7, 12, 4],     # Root, fifth, octave, third
            'minor': [0, 7, 12, 3]      # Root, fifth, octave, minor third
        },
        'funk': {
            'major': [0, 5, 7, 10],     # Root, fourth, fifth, seventh
            'minor': [0, 5, 7, 10]      # Root, fourth, fifth, minor seventh
        },
        'latin': {
            'major': [0, 5, 8, 12],     # Root, fourth, augmented fifth, octave
            'minor': [0, 5, 7, 12]      # Root, fourth, fifth, octave
        }
    }
    
    def __init__(self, midi_channel: int = 2, velocity: int = 100):
        """Initialize the bass.
        
        Args:
            midi_channel: MIDI channel number (0-15)
            velocity: Default note velocity (0-127)
        """
        super().__init__("Bass", midi_channel, velocity)
        self._last_note = None
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
            MIDI note number for the root note (C2 = 36)
            
        Raises:
            ValueError: If key string is invalid
        """
        # Remove any accidentals (sharp/flat)
        key_str = key_str.strip().upper()
        root = key_str[0]
        
        # Define MIDI note numbers for root notes (using C2 = 36 for bass)
        root_notes = {
            'C': 36,  # C2
            'D': 38,
            'E': 40,
            'F': 41,
            'G': 43,
            'A': 45,
            'B': 47
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
        """Get the playable MIDI note range for bass.
        
        Returns:
            Tuple of (lowest_note, highest_note) in MIDI note numbers
        """
        return (28, 67)  # E1 to G4
    
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
        # Handle chord notation - for bass, we only take the lowest note
        if note_str.startswith('[') and note_str.endswith(']'):
            chord_notes = note_str[1:-1].split(',')
            # Parse all notes and take the lowest one
            midi_notes = [self._parse_single_note(note.strip()) for note in chord_notes]
            return [min(midi_notes)]
        
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

    def _get_bass_line(self, root_note: int, scale: List[int], style: str, is_minor: bool) -> List[int]:
        """Get appropriate bass line based on style and scale.
        
        Args:
            root_note: MIDI note number of the root note
            scale: List of scale degrees
            style: Musical style/genre
            is_minor: Whether the key is minor
            
        Returns:
            List of MIDI note numbers for the bass line
        """
        mode = 'minor' if is_minor else 'major'
        
        if style == 'jazz':
            # Walking bass line for jazz
            pattern = self.BASS_PATTERNS['walking'][mode]
            return [root_note + n for n in pattern]
        elif style == 'funk':
            # Syncopated funk pattern
            pattern = self.BASS_PATTERNS['funk'][mode]
            return [root_note + n for n in pattern]
        elif style == 'latin':
            # Latin groove pattern
            pattern = self.BASS_PATTERNS['latin'][mode]
            return [root_note + n for n in pattern]
        else:
            # Default to basic groove pattern
            pattern = self.BASS_PATTERNS['groove'][mode]
            return [root_note + n for n in pattern]
            
    def _create_rhythmic_pattern(self, style: str, tempo: float) -> List[Tuple[float, float, float]]:
        """Create a rhythmic pattern based on style and tempo.
        
        Args:
            style: Musical style/genre
            tempo: Tempo in BPM
            
        Returns:
            List of (start_time, duration, velocity_multiplier) tuples
        """
        if style == 'jazz':
            # Walking bass pattern
            return [(i * 0.5, 0.5, 0.8) for i in range(8)]
        elif style == 'funk':
            # Sixteenth note funk pattern
            pattern = []
            for i in range(16):
                if i % 4 == 0:
                    pattern.append((i * 0.25, 0.25, 1.0))  # Strong beat
                elif i % 2 == 0:
                    pattern.append((i * 0.25, 0.25, 0.8))  # Medium beat
                else:
                    pattern.append((i * 0.25, 0.25, 0.6))  # Weak beat
            return pattern
        elif style == 'latin':
            # Syncopated Latin pattern
            return [
                (0.0, 0.5, 1.0),    # Strong beat
                (1.0, 0.25, 0.8),   # Syncopation
                (1.5, 0.25, 0.7),
                (2.0, 0.5, 0.9),    # Secondary strong beat
                (3.0, 0.25, 0.8),   # Syncopation
                (3.5, 0.25, 0.7)
            ]
        else:
            # Basic rock/pop pattern
            return [
                (0.0, 1.0, 1.0),    # Strong beat
                (1.0, 1.0, 0.8),    # Weak beat
                (2.0, 1.0, 0.9),    # Medium beat
                (3.0, 1.0, 0.8)     # Weak beat
            ]

    def generate_pattern(self, song_data: SongData, chord: str = None, style: str = None) -> List[Tuple[int, float, float, int]]:
        """Generate bass pattern that's compatible with the sample song.
        
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
            elif style == 'funk':
                base_adjustment *= 0.7  # Even shorter for funk
                
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
            # Simple root notes
            lambda t, i: [(validate_note(key_root), t, 1.0, 45)] if i % 2 == 0 else [],
            # Root and fifth
            lambda t, i: [(validate_note(key_root), t, 1.0, 50), 
                         (validate_note(key_root + 7), t + 1.0, 1.0, 45)] if i % 2 == 0 else [],
            # Walking pattern
            lambda t, i: [(validate_note(note), t + time, dur, int(vel * 100))
                         for time, dur, vel in self._create_rhythmic_pattern(style or 'rock', tempo)
                         for note in self._get_bass_line(key_root, scale, style or 'rock', is_minor)]
        ]
        
        verse_patterns = [
            # Groove pattern
            lambda t, i: [(validate_note(note), t + time, dur, int(vel * 100))
                         for time, dur, vel in self._create_rhythmic_pattern(style or 'rock', tempo)
                         for note in self._get_bass_line(key_root, scale, style or 'rock', is_minor)],
            # Root-fifth pattern
            lambda t, i: [(validate_note(key_root), t, 0.5, 65),
                         (validate_note(key_root + 7), t + 0.5, 0.5, 60)] if i % 2 == 0 else [],
            # Walking line
            lambda t, i: [(validate_note(key_root + scale[i % len(scale)]), t, 0.5, 60)]
        ]
        
        chorus_patterns = [
            # Strong root notes
            lambda t, i: [(validate_note(key_root), t, 1.0, 75)] if i % 2 == 0 else [],
            # Energetic pattern
            lambda t, i: [(validate_note(note), t + time, dur, int(vel * 100))
                         for time, dur, vel in self._create_rhythmic_pattern('funk', tempo)
                         for note in self._get_bass_line(key_root, scale, 'funk', is_minor)],
            # Root and octave
            lambda t, i: [(validate_note(key_root), t, 0.5, 75),
                         (validate_note(key_root + 12), t + 0.5, 0.5, 70)] if i % 2 == 0 else []
        ]
        
        bridge_patterns = [
            # Complex walking pattern
            lambda t, i: [(validate_note(note), t + time, dur, int(vel * 100))
                         for time, dur, vel in self._create_rhythmic_pattern('jazz', tempo)
                         for note in self._get_bass_line(key_root, scale, 'jazz', is_minor)],
            # Syncopated pattern
            lambda t, i: [(validate_note(key_root), t, 0.5, 65),
                         (validate_note(key_root + 7), t + 0.75, 0.25, 60)] if i % 2 == 0 else [],
            # Scale runs
            lambda t, i: [(validate_note(key_root + scale[i % len(scale)]), t, 0.25, 65)]
        ]
        
        outro_patterns = [
            # Fading pattern
            lambda t, i: [(validate_note(note), t + time, dur, int(vel * 100 * max(0.3, 1.0 - (i / 16))))
                         for time, dur, vel in self._create_rhythmic_pattern(style or 'rock', tempo)
                         for note in self._get_bass_line(key_root, scale, style or 'rock', is_minor)],
            # Simple resolution
            lambda t, i: [(validate_note(key_root), t, 2.0, max(30, 70 - (i // 4) * 10))] if i % 4 == 0 else [],
            # Final notes
            lambda t, i: [(validate_note(key_root), t, 1.0, max(30, 60 - (i // 2) * 5)),
                         (validate_note(key_root - 12), t + 1.0, 1.0, max(25, 55 - (i // 2) * 5))] if i % 2 == 0 else []
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
                
                # Add events with adjusted durations
                for note, time, duration, velocity in new_events:
                    adjusted_duration = adjust_duration(duration)
                    if time + adjusted_duration <= section.end_time:
                        events.append((note, time, adjusted_duration, velocity))
                
                current_time += 1.0  # Move to next beat
                pattern_index += 1
        
        return events 