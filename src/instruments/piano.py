"""Piano instrument implementation."""

from typing import List, Any, Tuple, Dict
from .base import BaseInstrument
from ..core.song_parser import SongData, Section
from ..patterns.pattern_manager import PatternManager
from ..patterns.variation_manager import VariationManager, VariationType

class Piano(BaseInstrument):
    """Piano instrument class."""
    
    # MIDI note numbers for basic chords
    CHORD_NOTES = {
        'C': [60, 64, 67],    # C4, E4, G4
        'Dm': [62, 65, 69],   # D4, F4, A4
        'Em': [64, 67, 71],   # E4, G4, B4
        'F': [65, 69, 72],    # F4, A4, C5
        'G': [67, 71, 74],    # G4, B4, D5
        'Am': [69, 72, 76],   # A4, C5, E5
        'Bdim': [71, 74, 77], # B4, D5, F5
    }
    
    def __init__(self, midi_channel: int = 0, velocity: int = 100):
        """Initialize the piano.
        
        Args:
            midi_channel: MIDI channel number (0-15)
            velocity: Default note velocity (0-127)
        """
        super().__init__("Piano", midi_channel, velocity)
        self._last_chord = None
        self._last_time = 0.0
        self._pattern_manager = PatternManager()
        self._variation_manager = VariationManager()
        self._song_length = 0.0
        self._last_pattern_time = 0.0
        self._min_pattern_interval = 4.0  # Minimum beats between pattern applications
    
    def get_playable_range(self) -> tuple[int, int]:
        """Get the playable MIDI note range for piano.
        
        Returns:
            Tuple of (lowest_note, highest_note) in MIDI note numbers
        """
        return (21, 108)  # A0 to C8
    
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
    
    def _dynamic_to_velocity(self, dynamic: str) -> int:
        """Convert dynamic marking to velocity.
        
        Args:
            dynamic: Dynamic marking (pp, p, mp, mf, f, ff)
            
        Returns:
            MIDI velocity (0-127)
        """
        dynamics = {
            'pp': 30,
            'p': 50,
            'mp': 70,
            'mf': 85,
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
    
    def _get_chord_for_note(self, note: int) -> str:
        """Determine the most appropriate chord for a given note."""
        # Convert MIDI note to note name (C4 = 60)
        note_name = (note - 60) % 12
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        # Simple chord selection based on note
        if note_name in [0, 4, 7]:  # C, E, G
            return 'C'
        elif note_name in [2, 5, 9]:  # D, F, A
            return 'Dm'
        elif note_name in [4, 7, 11]:  # E, G, B
            return 'Em'
        elif note_name in [5, 9, 0]:  # F, A, C
            return 'F'
        elif note_name in [7, 11, 2]:  # G, B, D
            return 'G'
        elif note_name in [9, 0, 4]:  # A, C, E
            return 'Am'
        else:
            return 'C'  # Default to C major
    
    def _apply_pattern(self, pattern: Dict[str, Any], base_time: float, chord: str) -> List[Tuple[int, float, float, int]]:
        """Apply a pattern starting at the given time with the specified chord."""
        events = []
        chord_notes = self.CHORD_NOTES.get(chord, self.CHORD_NOTES['C'])
        
        for note_event in pattern['notes']:
            time = base_time + note_event['beat']
            # Skip if we're beyond the song length
            if time >= self._song_length:
                continue
                
            duration = self._duration_to_beats(note_event['duration'])
            velocity = self._dynamic_to_velocity(note_event['dynamic'])
            
            # Transpose pattern notes to match the current chord
            for note_str in note_event['notes']:
                note = self._parse_single_note(note_str)
                # Calculate offset from C
                offset = note - 60  # C4 = 60
                # Apply offset to each chord note
                for chord_note in chord_notes:
                    events.append((chord_note + offset, time, duration, velocity))
        
        return events
    
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
    
    def _get_variation_types_for_section(self, section: Section) -> List[VariationType]:
        """Determine which variation types to apply based on section type."""
        if not section:
            return [VariationType.RHYTHMIC_ALTERATION]
            
        types = []
        if "intro" in section.name.lower():
            types.extend([VariationType.RHYTHMIC_ALTERATION, VariationType.MOOD_ADJUSTMENT])
        elif "verse" in section.name.lower():
            types.extend([VariationType.RHYTHMIC_ALTERATION])
        elif "chorus" in section.name.lower():
            types.extend([VariationType.KEY_TRANSPOSITION, VariationType.MOOD_ADJUSTMENT])
        elif "bridge" in section.name.lower():
            types.extend([VariationType.KEY_TRANSPOSITION, VariationType.RHYTHMIC_ALTERATION])
        else:
            types.append(VariationType.RHYTHMIC_ALTERATION)
        return types

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

    def _parse_key_root(self, key_str: str) -> int:
        """Parse a key string into a MIDI note number.
        
        Args:
            key_str: Key string (e.g., "E", "F#", "Bb")
            
        Returns:
            MIDI note number for the key root in octave 4
        """
        # Remove any whitespace and take just the first character
        note_name = key_str.strip()[0].upper()
        
        # Base note values in octave 4
        base_notes = {'C': 60, 'D': 62, 'E': 64, 'F': 65, 'G': 67, 'A': 69, 'B': 71}
        
        return base_notes[note_name]

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

    def generate_pattern(self, song_data: SongData, chord: str = None, style: str = None) -> List[Tuple[int, float, float, int]]:
        """Generate piano pattern that's compatible with the sample song.
        
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
            # Pattern 1: Sparse, atmospheric
            lambda t, i: [(key_root, t, 2.0, 50), (key_root + 7, t, 2.0, 45)] if i % 4 == 0 else [],
            # Pattern 2: Arpeggiated
            lambda t, i: [(key_root + scale[i % len(scale)], t, 1.0, 45)] if i % 2 == 0 else [],
            # Pattern 3: Chordal with space
            lambda t, i: [(key_root, t, 1.0, 50), (key_root + 4, t, 1.0, 45), (key_root + 7, t, 1.0, 45)] if i % 4 == 0 else [],
            # Pattern 4: Alternating octaves
            lambda t, i: [(key_root, t, 1.0, 45), (key_root + 12, t + 0.5, 1.0, 40)] if i % 2 == 0 else [],
            # Pattern 5: Single note with echo
            lambda t, i: [(key_root, t, 1.0, 50), (key_root, t + 0.5, 0.5, 35)] if i % 2 == 0 else []
        ]
        
        verse_patterns = [
            # Pattern 1: Flowing accompaniment
            lambda t, i: [(key_root, t, 1.0, 60), (key_root + 4, t, 1.0, 55), (key_root + 7, t, 1.0, 55)] if i % 2 == 0 else [],
            # Pattern 2: Syncopated
            lambda t, i: [(key_root, t, 0.5, 60), (key_root + 7, t + 0.25, 0.5, 55)] if i % 2 == 0 else [],
            # Pattern 3: Broken chords
            lambda t, i: [(key_root + scale[i % len(scale)], t, 0.5, 55)] if i % 2 == 0 else [],
            # Pattern 4: Walking bass with chords
            lambda t, i: [(key_root + scale[i % len(scale)], t, 0.5, 55), (key_root + 4, t + 0.25, 0.5, 50), (key_root + 7, t + 0.5, 0.5, 50)] if i % 2 == 0 else [],
            # Pattern 5: Alternating intervals
            lambda t, i: [(key_root, t, 0.5, 60), (key_root + 4, t + 0.25, 0.5, 55), (key_root + 7, t + 0.5, 0.5, 55)] if i % 2 == 0 else []
        ]
        
        chorus_patterns = [
            # Pattern 1: Full chords
            lambda t, i: [(key_root, t, 1.0, 75), (key_root + 4, t, 1.0, 70), (key_root + 7, t, 1.0, 70), (key_root + 12, t, 1.0, 65)] if i % 2 == 0 else [],
            # Pattern 2: Octave-based
            lambda t, i: [(key_root, t, 1.0, 75), (key_root + 12, t, 1.0, 70), (key_root + 7, t + 0.5, 0.5, 65)] if i % 2 == 0 else [],
            # Pattern 3: Power chords
            lambda t, i: [(key_root, t, 1.0, 80), (key_root + 7, t, 1.0, 75), (key_root + 12, t, 1.0, 70)] if i % 2 == 0 else [],
            # Pattern 4: Staccato chords
            lambda t, i: [(key_root, t, 0.5, 80), (key_root + 4, t, 0.5, 75), (key_root + 7, t, 0.5, 75)] if i % 2 == 0 else [],
            # Pattern 5: Rolling arpeggios
            lambda t, i: [(key_root + scale[i % len(scale)], t, 0.5, 75), (key_root + scale[(i + 1) % len(scale)], t + 0.25, 0.5, 70)] if i % 2 == 0 else []
        ]
        
        bridge_patterns = [
            # Pattern 1: Contrasting chords
            lambda t, i: [(key_root + 5 if i % 8 == 0 else key_root + 7, t, 2.0, 65), (key_root + 9 if i % 8 == 0 else key_root + 11, t, 2.0, 60)] if i % 4 == 0 else [],
            # Pattern 2: Chromatic movement
            lambda t, i: [(key_root + scale[i % len(scale)], t, 1.0, 65)] if i % 2 == 0 else [],
            # Pattern 3: Suspended chords
            lambda t, i: [(key_root + 5, t, 1.0, 65), (key_root + 9, t, 1.0, 60), (key_root + 11, t, 1.0, 60)] if i % 2 == 0 else [],
            # Pattern 4: Alternating inversions
            lambda t, i: [(key_root + 7, t, 1.0, 65), (key_root + 4, t + 0.5, 1.0, 60), (key_root, t + 1.0, 1.0, 55)] if i % 4 == 0 else [],
            # Pattern 5: Dissonant intervals
            lambda t, i: [(key_root + 1, t, 1.0, 65), (key_root + 6, t + 0.5, 1.0, 60)] if i % 2 == 0 else []
        ]
        
        outro_patterns = [
            # Pattern 1: Fading chords
            lambda t, i: [(key_root, t, 2.0, max(30, 70 - (i // 4) * 10)), (key_root + 7, t, 2.0, max(25, 65 - (i // 4) * 10))] if i % 4 == 0 else [],
            # Pattern 2: Dwindling arpeggio
            lambda t, i: [(key_root + scale[i % len(scale)], t, 1.0, max(30, 70 - (i // 2) * 5))] if i % 2 == 0 else [],
            # Pattern 3: Simple resolution
            lambda t, i: [(key_root, t, 2.0, max(30, 70 - (i // 4) * 10))] if i % 4 == 0 else [],
            # Pattern 4: Echoing notes
            lambda t, i: [(key_root, t, 1.0, max(30, 70 - (i // 2) * 5)), (key_root, t + 0.5, 0.5, max(20, 60 - (i // 2) * 5))] if i % 2 == 0 else [],
            # Pattern 5: Fading intervals
            lambda t, i: [(key_root, t, 1.0, max(30, 70 - (i // 2) * 5)), (key_root + 4, t + 0.5, 1.0, max(25, 65 - (i // 2) * 5))] if i % 2 == 0 else []
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