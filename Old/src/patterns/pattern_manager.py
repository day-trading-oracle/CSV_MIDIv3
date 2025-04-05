"""Pattern manager for handling musical patterns."""

from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import re

class PatternManager:
    """Manages musical patterns for different instruments and genres."""
    
    def __init__(self, cache_size: int = 100):
        """Initialize the pattern manager.
        
        Args:
            cache_size: Maximum number of patterns to cache.
        """
        self._cache_size = cache_size
        self._pattern_cache: Dict[str, Dict[str, Any]] = {}
        self._patterns_dir = Path(__file__).parent / "instrument_patterns"
    
    def _parse_note_line(self, line: str) -> Tuple[float, List[str], str, str]:
        """Parse a note line from the pattern file.
        
        Args:
            line: Line containing note information.
            
        Returns:
            Tuple of (beat, notes, dynamic, duration).
        """
        # Format: "1.0: C4,E4,G4 (mf, quarter)"
        beat_str, rest = line.split(':', 1)
        beat = float(beat_str.strip())
        
        # Split notes and properties
        notes_str, props = rest.split('(')
        notes = [note.strip() for note in notes_str.split(',')]
        
        # Get dynamic and duration
        dynamic, duration = props.rstrip(')').split(',')
        return beat, notes, dynamic.strip(), duration.strip()
    
    def _parse_pattern_file(self, file_path: Path, target_genre: str) -> Optional[Dict[str, Any]]:
        """Parse a pattern file and extract pattern for the target genre.
        
        Args:
            file_path: Path to the pattern file.
            target_genre: The genre to extract.
            
        Returns:
            Dictionary containing the pattern data, or None if not found.
        """
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            current_pattern = None
            current_genre = None
            patterns = {}
            notes = []
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Check for pattern header
                if line.startswith('[') and line.endswith(']'):
                    if current_pattern and current_genre == target_genre.lower():
                        patterns[current_pattern] = {
                            'title': current_pattern,
                            'genre': current_genre,
                            'time_signature': time_signature,
                            'notes': notes
                        }
                    current_pattern = line[1:-1]
                    notes = []
                    continue
                
                # Parse pattern properties
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == 'Genre':
                        current_genre = value.lower()
                    elif key == 'Time Signature':
                        num, den = value.split('/')
                        time_signature = (int(num), int(den))
                    elif key == 'Notes':
                        continue  # Skip the "Notes:" header
                    else:
                        # Parse note line
                        try:
                            beat, note_list, dynamic, duration = self._parse_note_line(line)
                            notes.append({
                                'beat': beat,
                                'notes': note_list,
                                'dynamic': dynamic,
                                'duration': duration
                            })
                        except ValueError:
                            continue
            
            # Add the last pattern if it matches the target genre
            if current_pattern and current_genre == target_genre.lower():
                patterns[current_pattern] = {
                    'title': current_pattern,
                    'genre': current_genre,
                    'time_signature': time_signature,
                    'notes': notes
                }
            
            # Return the first pattern for the genre
            return next(iter(patterns.values())) if patterns else None
            
        except (FileNotFoundError, ValueError) as e:
            print(f"Error reading pattern file {file_path}: {str(e)}")
            return None
    
    def get_pattern(self, instrument: str, genre: str) -> Optional[Dict[str, Any]]:
        """Get a pattern for the specified instrument and genre.
        
        Args:
            instrument: The instrument name.
            genre: The musical genre.
            
        Returns:
            A dictionary containing the pattern data, or None if not found.
        """
        cache_key = f"{instrument}_{genre}"
        
        # Check cache first
        if cache_key in self._pattern_cache:
            return self._pattern_cache[cache_key]
        
        # Load from file
        pattern_file = self._patterns_dir / f"{instrument.lower()}.txt"
        if not pattern_file.exists():
            print(f"Pattern file not found: {pattern_file}")
            return None
        
        pattern = self._parse_pattern_file(pattern_file, genre)
        if pattern:
            # Cache the pattern
            if len(self._pattern_cache) >= self._cache_size:
                # Remove oldest entry
                self._pattern_cache.pop(next(iter(self._pattern_cache)))
            self._pattern_cache[cache_key] = pattern
        
        return pattern
    
    def cleanup(self):
        """Clean up resources."""
        self._pattern_cache.clear() 