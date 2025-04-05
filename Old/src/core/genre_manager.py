"""Genre manager for handling musical genres and their characteristics."""

from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import json

class GenreManager:
    """Manages musical genre definitions and their characteristics."""
    
    def __init__(self):
        """Initialize the genre manager."""
        self._genres_dir = Path(__file__).parent.parent / "genres" / "genre_definitions"
        self._genres: Dict[str, Dict[str, Any]] = {}
        self._load_genres()
    
    def _load_genres(self) -> None:
        """Load genre definitions from JSON files."""
        for genre_file in self._genres_dir.glob("*.json"):
            try:
                with open(genre_file, 'r') as f:
                    genre_data = json.load(f)
                    genre_name = genre_file.stem.lower()
                    self._genres[genre_name] = genre_data
            except Exception as e:
                print(f"Error loading genre file {genre_file}: {e}")
    
    def get_genre(self, genre_name: str) -> Optional[Dict[str, Any]]:
        """Get the characteristics of a specific genre.
        
        Args:
            genre_name: Name of the genre to get.
            
        Returns:
            Dictionary containing genre characteristics, or None if not found.
        """
        return self._genres.get(genre_name.lower())
    
    def get_available_genres(self) -> List[str]:
        """Get a list of all available genres.
        
        Returns:
            List of genre names.
        """
        return list(self._genres.keys())
    
    def get_genre_characteristics(self, genre_name: str) -> Dict[str, Any]:
        """Get the musical characteristics of a genre.
        
        Args:
            genre_name: Name of the genre.
            
        Returns:
            Dictionary containing genre characteristics.
        """
        genre = self.get_genre(genre_name)
        if not genre:
            return {}
        
        return {
            'tempo_range': genre.get('tempo_range', (60, 180)),
            'time_signatures': genre.get('time_signatures', [(4, 4)]),
            'common_chords': genre.get('common_chords', []),
            'instrumentation': genre.get('instrumentation', {}),
            'rhythm_patterns': genre.get('rhythm_patterns', {}),
            'dynamics': genre.get('dynamics', {}),
            'articulation': genre.get('articulation', {}),
            'form': genre.get('form', {})
        }
    
    def get_instrument_characteristics(self, genre_name: str, instrument: str) -> Dict[str, Any]:
        """Get the characteristics of an instrument in a specific genre.
        
        Args:
            genre_name: Name of the genre.
            instrument: Name of the instrument.
            
        Returns:
            Dictionary containing instrument characteristics.
        """
        genre = self.get_genre(genre_name)
        if not genre:
            return {}
        
        return genre.get('instrumentation', {}).get(instrument.lower(), {})
    
    def get_rhythm_pattern(self, genre_name: str, instrument: str) -> Dict[str, Any]:
        """Get the rhythm pattern for an instrument in a genre.
        
        Args:
            genre_name: Name of the genre.
            instrument: Name of the instrument.
            
        Returns:
            Dictionary containing rhythm pattern.
        """
        genre = self.get_genre(genre_name)
        if not genre:
            return {}
        
        return genre.get('rhythm_patterns', {}).get(instrument.lower(), {})
    
    def cleanup(self) -> None:
        """Clean up any resources used by the genre manager."""
        self._genres.clear() 