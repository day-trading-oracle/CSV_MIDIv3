"""
Genre management module for MIDI music generation.
"""

class GenreManager:
    """
    Manages musical genres and their associated properties.
    """
    
    def __init__(self):
        """Initialize the genre manager with default genres."""
        self.genres = {
            'classical': {
                'tempo_range': (60, 120),
                'instruments': {
                    'piano': 0,  # Acoustic Grand Piano
                    'bass': 32,  # Acoustic Bass
                    'strings': 48,  # String Ensemble 1
                },
                'articulations': ['staccato', 'legato', 'accent'],
            },
            'jazz': {
                'tempo_range': (80, 160),
                'instruments': {
                    'piano': 0,  # Acoustic Grand Piano
                    'bass': 32,  # Acoustic Bass
                    'drums': 128,  # Standard Kit
                    'saxophone': 65,  # Alto Sax
                },
                'articulations': ['swing', 'staccato', 'accent'],
            },
            'rock': {
                'tempo_range': (90, 180),
                'instruments': {
                    'guitar': 27,  # Electric Guitar (clean)
                    'bass': 33,  # Electric Bass (finger)
                    'drums': 128,  # Standard Kit
                },
                'articulations': ['palm_mute', 'bend', 'slide'],
            },
            'pop': {
                'tempo_range': (90, 130),
                'instruments': {
                    'piano': 0,  # Acoustic Grand Piano
                    'bass': 33,  # Electric Bass (finger)
                    'guitar': 27,  # Electric Guitar (clean)
                    'drums': 128,  # Standard Kit
                },
                'articulations': ['staccato', 'accent'],
            },
        }
    
    def get_genre_properties(self, genre: str) -> dict:
        """
        Get the properties for a specific genre.
        
        Args:
            genre: The name of the genre
            
        Returns:
            A dictionary containing the genre's properties
        """
        return self.genres.get(genre, self.genres['pop'])  # Default to pop if genre not found
    
    def get_instrument_program(self, genre: str, instrument: str) -> int:
        """
        Get the MIDI program number for an instrument in a specific genre.
        
        Args:
            genre: The name of the genre
            instrument: The name of the instrument
            
        Returns:
            The MIDI program number for the instrument
        """
        genre_props = self.get_genre_properties(genre)
        return genre_props['instruments'].get(instrument, 0)  # Default to piano if instrument not found
    
    def get_tempo_range(self, genre: str) -> tuple:
        """
        Get the typical tempo range for a genre.
        
        Args:
            genre: The name of the genre
            
        Returns:
            A tuple of (min_tempo, max_tempo)
        """
        genre_props = self.get_genre_properties(genre)
        return genre_props['tempo_range']
    
    def get_articulations(self, genre: str) -> list:
        """
        Get the common articulations used in a genre.
        
        Args:
            genre: The name of the genre
            
        Returns:
            A list of articulation names
        """
        genre_props = self.get_genre_properties(genre)
        return genre_props['articulations'] 