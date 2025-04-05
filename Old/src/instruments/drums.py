"""Drums instrument implementation."""

from typing import List, Any, Tuple, Dict
from .base import BaseInstrument
from ..core.song_parser import SongData, Section
from ..patterns.pattern_manager import PatternManager
from ..patterns.variation_manager import VariationManager, VariationType

class Drums(BaseInstrument):
    """Drums instrument class."""
    
    # MIDI note numbers for drum sounds
    DRUM_NOTES = {
        'kick': 36,      # C1
        'snare': 38,     # D1
        'hihat': 42,     # F#1
        'tom1': 45,      # A1
        'tom2': 47,      # B1
        'crash': 49,     # C#2
        'ride': 51,      # D#2
        'clap': 39,      # D#1
        'rim': 37,       # C#1
        'shaker': 70,    # A#3
        'tambourine': 54 # F#2
    }
    
    def __init__(self, midi_channel: int = 9, velocity: int = 100):
        """Initialize the drums.
        
        Args:
            midi_channel: MIDI channel number (0-15)
            velocity: Default note velocity (0-127)
        """
        super().__init__("Drums", midi_channel, velocity)
        self._pattern_manager = PatternManager()
        self._variation_manager = VariationManager()
        self._song_length = 0.0
        self._last_pattern_time = 0.0
        self._min_pattern_interval = 4.0  # Minimum beats between pattern applications

    def get_playable_range(self) -> tuple[int, int]:
        """Get the playable MIDI note range for drums.
        
        Returns:
            Tuple of (lowest_note, highest_note) in MIDI note numbers
        """
        # For drums, we use the standard MIDI drum kit range
        # This is typically from C1 (36) to A#3 (70)
        return (36, 70)

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
        """Generate drum pattern that's compatible with the sample song.
        
        Args:
            song_data: Song data containing the sample song's structure
            chord: Optional chord to use as base (ignored for drums)
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
        
        # Define possible patterns for each section type with more variations
        intro_patterns = [
            # Pattern 1: Simple kick and hihat
            lambda t, i: [(self.DRUM_NOTES['kick'], t, 0.25, 80), (self.DRUM_NOTES['hihat'], t, 0.25, 60)] if i % 2 == 0 else [],
            # Pattern 2: Kick, snare, and hihat
            lambda t, i: [(self.DRUM_NOTES['kick'], t, 0.25, 80), (self.DRUM_NOTES['snare'], t + 0.5, 0.25, 70), (self.DRUM_NOTES['hihat'], t, 0.25, 60)] if i % 2 == 0 else [],
            # Pattern 3: Kick and ride
            lambda t, i: [(self.DRUM_NOTES['kick'], t, 0.25, 80), (self.DRUM_NOTES['ride'], t, 0.25, 65)] if i % 2 == 0 else [],
            # Pattern 4: Kick, clap, and shaker
            lambda t, i: [(self.DRUM_NOTES['kick'], t, 0.25, 80), (self.DRUM_NOTES['clap'], t + 0.5, 0.25, 70), (self.DRUM_NOTES['shaker'], t, 0.25, 55)] if i % 2 == 0 else [],
            # Pattern 5: Kick, rim, and tambourine
            lambda t, i: [(self.DRUM_NOTES['kick'], t, 0.25, 80), (self.DRUM_NOTES['rim'], t + 0.5, 0.25, 70), (self.DRUM_NOTES['tambourine'], t, 0.25, 60)] if i % 2 == 0 else []
        ]
        
        verse_patterns = [
            # Pattern 1: Standard rock beat
            lambda t, i: [(self.DRUM_NOTES['kick'], t, 0.25, 80), (self.DRUM_NOTES['snare'], t + 0.5, 0.25, 70), (self.DRUM_NOTES['hihat'], t, 0.25, 60)] if i % 2 == 0 else [],
            # Pattern 2: Kick, snare, and ride
            lambda t, i: [(self.DRUM_NOTES['kick'], t, 0.25, 80), (self.DRUM_NOTES['snare'], t + 0.5, 0.25, 70), (self.DRUM_NOTES['ride'], t, 0.25, 65)] if i % 2 == 0 else [],
            # Pattern 3: Kick, clap, and hihat
            lambda t, i: [(self.DRUM_NOTES['kick'], t, 0.25, 80), (self.DRUM_NOTES['clap'], t + 0.5, 0.25, 70), (self.DRUM_NOTES['hihat'], t, 0.25, 60)] if i % 2 == 0 else [],
            # Pattern 4: Kick, snare, and shaker
            lambda t, i: [(self.DRUM_NOTES['kick'], t, 0.25, 80), (self.DRUM_NOTES['snare'], t + 0.5, 0.25, 70), (self.DRUM_NOTES['shaker'], t, 0.25, 55)] if i % 2 == 0 else [],
            # Pattern 5: Kick, rim, and tambourine
            lambda t, i: [(self.DRUM_NOTES['kick'], t, 0.25, 80), (self.DRUM_NOTES['rim'], t + 0.5, 0.25, 70), (self.DRUM_NOTES['tambourine'], t, 0.25, 60)] if i % 2 == 0 else []
        ]
        
        chorus_patterns = [
            # Pattern 1: Full rock beat with crash
            lambda t, i: [(self.DRUM_NOTES['kick'], t, 0.25, 90), (self.DRUM_NOTES['snare'], t + 0.5, 0.25, 80), (self.DRUM_NOTES['hihat'], t, 0.25, 70), (self.DRUM_NOTES['crash'], t, 0.25, 85)] if i % 2 == 0 else [],
            # Pattern 2: Kick, snare, and ride with crash
            lambda t, i: [(self.DRUM_NOTES['kick'], t, 0.25, 90), (self.DRUM_NOTES['snare'], t + 0.5, 0.25, 80), (self.DRUM_NOTES['ride'], t, 0.25, 75), (self.DRUM_NOTES['crash'], t, 0.25, 85)] if i % 2 == 0 else [],
            # Pattern 3: Kick, clap, and hihat with crash
            lambda t, i: [(self.DRUM_NOTES['kick'], t, 0.25, 90), (self.DRUM_NOTES['clap'], t + 0.5, 0.25, 80), (self.DRUM_NOTES['hihat'], t, 0.25, 70), (self.DRUM_NOTES['crash'], t, 0.25, 85)] if i % 2 == 0 else [],
            # Pattern 4: Kick, snare, and shaker with crash
            lambda t, i: [(self.DRUM_NOTES['kick'], t, 0.25, 90), (self.DRUM_NOTES['snare'], t + 0.5, 0.25, 80), (self.DRUM_NOTES['shaker'], t, 0.25, 65), (self.DRUM_NOTES['crash'], t, 0.25, 85)] if i % 2 == 0 else [],
            # Pattern 5: Kick, rim, and tambourine with crash
            lambda t, i: [(self.DRUM_NOTES['kick'], t, 0.25, 90), (self.DRUM_NOTES['rim'], t + 0.5, 0.25, 80), (self.DRUM_NOTES['tambourine'], t, 0.25, 70), (self.DRUM_NOTES['crash'], t, 0.25, 85)] if i % 2 == 0 else []
        ]
        
        bridge_patterns = [
            # Pattern 1: Tom-based pattern
            lambda t, i: [(self.DRUM_NOTES['kick'], t, 0.25, 85), (self.DRUM_NOTES['tom1'], t + 0.5, 0.25, 75), (self.DRUM_NOTES['tom2'], t + 0.75, 0.25, 70), (self.DRUM_NOTES['hihat'], t, 0.25, 65)] if i % 2 == 0 else [],
            # Pattern 2: Kick, snare, and ride with toms
            lambda t, i: [(self.DRUM_NOTES['kick'], t, 0.25, 85), (self.DRUM_NOTES['snare'], t + 0.5, 0.25, 75), (self.DRUM_NOTES['ride'], t, 0.25, 70), (self.DRUM_NOTES['tom1'], t + 0.75, 0.25, 70)] if i % 2 == 0 else [],
            # Pattern 3: Kick, clap, and hihat with toms
            lambda t, i: [(self.DRUM_NOTES['kick'], t, 0.25, 85), (self.DRUM_NOTES['clap'], t + 0.5, 0.25, 75), (self.DRUM_NOTES['hihat'], t, 0.25, 65), (self.DRUM_NOTES['tom2'], t + 0.75, 0.25, 70)] if i % 2 == 0 else [],
            # Pattern 4: Kick, snare, and shaker with toms
            lambda t, i: [(self.DRUM_NOTES['kick'], t, 0.25, 85), (self.DRUM_NOTES['snare'], t + 0.5, 0.25, 75), (self.DRUM_NOTES['shaker'], t, 0.25, 60), (self.DRUM_NOTES['tom1'], t + 0.75, 0.25, 70)] if i % 2 == 0 else [],
            # Pattern 5: Kick, rim, and tambourine with toms
            lambda t, i: [(self.DRUM_NOTES['kick'], t, 0.25, 85), (self.DRUM_NOTES['rim'], t + 0.5, 0.25, 75), (self.DRUM_NOTES['tambourine'], t, 0.25, 65), (self.DRUM_NOTES['tom2'], t + 0.75, 0.25, 70)] if i % 2 == 0 else []
        ]
        
        outro_patterns = [
            # Pattern 1: Fading kick and hihat
            lambda t, i: [(self.DRUM_NOTES['kick'], t, 0.25, max(40, 80 - (i // 4) * 10)), (self.DRUM_NOTES['hihat'], t, 0.25, max(30, 60 - (i // 4) * 5))] if i % 2 == 0 else [],
            # Pattern 2: Kick, snare, and ride with fade
            lambda t, i: [(self.DRUM_NOTES['kick'], t, 0.25, max(40, 80 - (i // 4) * 10)), (self.DRUM_NOTES['snare'], t + 0.5, 0.25, max(35, 70 - (i // 4) * 8)), (self.DRUM_NOTES['ride'], t, 0.25, max(30, 65 - (i // 4) * 7))] if i % 2 == 0 else [],
            # Pattern 3: Kick, clap, and hihat with fade
            lambda t, i: [(self.DRUM_NOTES['kick'], t, 0.25, max(40, 80 - (i // 4) * 10)), (self.DRUM_NOTES['clap'], t + 0.5, 0.25, max(35, 70 - (i // 4) * 8)), (self.DRUM_NOTES['hihat'], t, 0.25, max(30, 60 - (i // 4) * 5))] if i % 2 == 0 else [],
            # Pattern 4: Kick, snare, and shaker with fade
            lambda t, i: [(self.DRUM_NOTES['kick'], t, 0.25, max(40, 80 - (i // 4) * 10)), (self.DRUM_NOTES['snare'], t + 0.5, 0.25, max(35, 70 - (i // 4) * 8)), (self.DRUM_NOTES['shaker'], t, 0.25, max(25, 55 - (i // 4) * 5))] if i % 2 == 0 else [],
            # Pattern 5: Kick, rim, and tambourine with fade
            lambda t, i: [(self.DRUM_NOTES['kick'], t, 0.25, max(40, 80 - (i // 4) * 10)), (self.DRUM_NOTES['rim'], t + 0.5, 0.25, max(35, 70 - (i // 4) * 8)), (self.DRUM_NOTES['tambourine'], t, 0.25, max(30, 60 - (i // 4) * 5))] if i % 2 == 0 else []
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
                    # Adjust duration based on tempo
                    adjusted_duration = adjust_duration(dur)
                    
                    # Ensure event doesn't extend beyond section
                    if t + adjusted_duration > section_end:
                        adjusted_duration = section_end - t
                    
                    # Only add if duration is positive
                    if adjusted_duration > 0:
                        events.append((note, t, adjusted_duration, vel))
        
        # Sort events by time
        events = sorted(events, key=lambda x: x[1])
        
        # Validate total pattern length
        if events:
            last_event_time = events[-1][1] + events[-1][2]  # last start time + duration
            if last_event_time < total_song_length:
                # Add sustaining hihat to fill the gap
                gap_start = last_event_time
                while gap_start < total_song_length:
                    # Add a sustaining hihat note
                    duration = min(0.25, total_song_length - gap_start)
                    events.append((self.DRUM_NOTES['hihat'], gap_start, duration, 45))  # Soft velocity for fill
                    gap_start += duration
            elif last_event_time > total_song_length:
                # Trim events that extend beyond song length
                events = [(n, t, min(d, total_song_length - t), v) for n, t, d, v in events if t < total_song_length]
        
        return events 