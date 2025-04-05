"""Base class for all musical instruments."""

import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pathlib import Path

class BaseInstrument(ABC):
    """Abstract base class for all musical instruments."""
    
    def __init__(self, name: str, midi_channel: int, velocity: int = 100):
        """Initialize the base instrument.
        
        Args:
            name: Name of the instrument
            midi_channel: MIDI channel number (0-15)
            velocity: Default note velocity (0-127)
        """
        self.name = name
        self.midi_channel = midi_channel
        self.velocity = velocity
        self._patterns: Dict[str, List[Any]] = {}
        self._variations: Dict[str, List[Any]] = {}
        self._load_patterns()
    
    def _load_patterns(self) -> None:
        """Load patterns from JSON files."""
        patterns_dir = Path(__file__).parent.parent / "patterns" / "instrument_patterns"
        
        # Load base patterns
        base_pattern_file = patterns_dir / f"{self.name.lower()}.json"
        if base_pattern_file.exists():
            with open(base_pattern_file, 'r') as f:
                self._patterns = json.load(f)
        
        # Load variations
        variations_file = patterns_dir / f"{self.name.lower()}_variations.json"
        if variations_file.exists():
            with open(variations_file, 'r') as f:
                self._variations = json.load(f)
    
    @abstractmethod
    def get_playable_range(self) -> tuple[int, int]:
        """Get the playable MIDI note range for this instrument.
        
        Returns:
            Tuple of (lowest_note, highest_note) in MIDI note numbers
        """
        pass
    
    @abstractmethod
    def generate_pattern(self, chord: str, style: str) -> List[Any]:
        """Generate a musical pattern for the given chord and style.
        
        Args:
            chord: Chord symbol (e.g., "C", "Am", "F#m7")
            style: Musical style (e.g., "jazz", "rock", "classical")
            
        Returns:
            List of MIDI events representing the pattern
        """
        pass
    
    def cleanup(self) -> None:
        """Clean up any resources used by the instrument."""
        self._patterns.clear()
        self._variations.clear() 