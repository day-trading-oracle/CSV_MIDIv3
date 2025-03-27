"""
Genre Manager for MusicMidi

This module provides genre-specific music generation capabilities for the MusicMidi application.
It defines different musical genres with their characteristic chord progressions, rhythmic patterns,
and instrument settings.
"""

import random
from abc import ABC, abstractmethod

class GenreBase(ABC):
    """Abstract base class for all musical genres"""
    
    def __init__(self, name):
        self.name = name
        # MIDI program numbers for instruments (0-127)
        self.instruments = {
            'melody': 0,  # Default: Acoustic Grand Piano
            'accompaniment': 0  # Default: Acoustic Grand Piano
        }
        
        # Characteristic chord progressions for this genre (scale degrees)
        self.chord_progressions = []
        
        # Rhythmic patterns for accompaniment [start_time, duration]
        self.rhythm_patterns = {}
        
        # Default tempo range
        self.tempo_range = (90, 120)
        
        # Dynamics characteristics
        self.dynamics = {
            'default': 'mf',
            'variation': 'low'  # low, medium, high
        }
        
        # Articulation patterns (mapping of note positions to articulations)
        self.articulations = {}
    
    @abstractmethod
    def get_accompaniment_pattern(self):
        """Return the appropriate accompaniment pattern for this genre"""
        pass
    
    def get_chord_progression(self, length=4):
        """Get a characteristic chord progression for this genre"""
        if not self.chord_progressions:
            # Default progression if none defined
            return [0, 4, 5, 3]  # I-V-vi-IV
            
        # Choose a random progression from the genre's options
        progression = random.choice(self.chord_progressions)
        
        # Extend if needed to reach the requested length
        while len(progression) < length:
            progression = progression + progression
        
        return progression[:length]
    
    def get_tempo(self):
        """Get a typical tempo for this genre"""
        return random.randint(self.tempo_range[0], self.tempo_range[1])
    
    def get_rhythm_pattern(self, pattern_type='basic'):
        """Get a rhythm pattern characteristic of this genre"""
        if pattern_type in self.rhythm_patterns:
            return self.rhythm_patterns[pattern_type]
        else:
            # Default quarter note pattern if requested type not available
            return [[i, 1.0] for i in range(4)]
    
    def get_instrument(self, part='accompaniment'):
        """Get the MIDI instrument number for a specific part"""
        return self.instruments.get(part, 0)  # Default to piano if not specified


class ClassicalGenre(GenreBase):
    """Base class for classical music genres"""
    
    def __init__(self, name="Classical"):
        super().__init__(name)
        # Common classical chord progressions
        self.chord_progressions = [
            [0, 4, 5, 3],  # I-V-vi-IV
            [0, 3, 4, 0],  # I-IV-V-I
            [5, 3, 0, 4],  # vi-IV-I-V
            [0, 4, 3, 4]   # I-V-IV-V
        ]
        
        # Rhythm patterns
        self.rhythm_patterns = {
            'alberti': [[0.0, 0.5], [0.5, 0.5], [1.0, 0.5], [1.5, 0.5],
                      [2.0, 0.5], [2.5, 0.5], [3.0, 0.5], [3.5, 0.5]],  # Alberti bass
            'block': [[0.0, 1.0], [1.0, 1.0], [2.0, 1.0], [3.0, 1.0]],  # Block chords
            'waltz': [[0.0, 1.0], [1.0, 0.5], [1.5, 0.5], [2.0, 0.5], [2.5, 0.5], [3.0, 1.0]]  # Waltz
        }
        
        # Classical instruments
        self.instruments = {
            'melody': 0,  # Acoustic Grand Piano
            'accompaniment': 0  # Acoustic Grand Piano
        }
        
        # Classical dynamics
        self.dynamics = {
            'default': 'mf',
            'variation': 'high'  # Classical music often has high dynamic range
        }
        
        self.tempo_range = (70, 120)
    
    def get_accompaniment_pattern(self):
        """Return a typical classical accompaniment pattern"""
        return 'alberti'  # Alberti bass is common in classical music


class BaroqueStyle(ClassicalGenre):
    """Baroque music style (1600-1750)"""
    
    def __init__(self):
        super().__init__("Baroque")
        # Baroque-specific chord progressions
        self.chord_progressions = [
            [0, 4, 5, 3],  # I-V-vi-IV
            [0, 5, 3, 6, 2, 5, 0],  # Circle of fifths progression
            [0, 0, 4, 4, 5, 5, 0, 0]  # I-I-V-V-vi-vi-I-I
        ]
        
        # Baroque instruments
        self.instruments = {
            'melody': 6,  # Harpsichord
            'accompaniment': 6  # Harpsichord
        }
        
        # Baroque uses more ornamentation
        self.articulations = {
            'trill': [0, 4, 8],
            'mordent': [2, 6, 10]
        }
        
        self.tempo_range = (80, 130)
    
    def get_accompaniment_pattern(self):
        """Return a typical baroque accompaniment pattern"""
        return random.choice(['alberti', 'block'])


class RomanticStyle(ClassicalGenre):
    """Romantic music style (1800-1910)"""
    
    def __init__(self):
        super().__init__("Romantic")
        # Romantic-specific chord progressions (more emotional)
        self.chord_progressions = [
            [0, 5, 3, 4],  # I-vi-IV-V
            [0, 5, 1, 4],  # I-vi-ii-V
            [0, 2, 5, 0]   # I-iii-vi-I
        ]
        
        # Romantic instruments - piano-focused
        self.instruments = {
            'melody': 0,  # Grand Piano
            'accompaniment': 0  # Grand Piano
        }
        
        self.tempo_range = (60, 110)
    
    def get_accompaniment_pattern(self):
        """Return a typical romantic accompaniment pattern"""
        return random.choice(['alberti', 'waltz'])


class PopGenre(GenreBase):
    """Base class for popular music genres"""
    
    def __init__(self, name="Pop"):
        super().__init__(name)
        # Common pop chord progressions
        self.chord_progressions = [
            [0, 4, 5, 3],  # I-V-vi-IV (most common pop progression)
            [0, 3, 4, 3],  # I-IV-V-IV
            [0, 3, 0, 4],  # I-IV-I-V
            [5, 3, 0, 4]   # vi-IV-I-V
        ]
        
        # Rhythm patterns
        self.rhythm_patterns = {
            'basic': [[0.0, 1.0], [1.0, 1.0], [2.0, 1.0], [3.0, 1.0]],
            'eighth': [[i*0.5, 0.5] for i in range(8)],
            'syncopated': [[0.0, 1.5], [1.5, 0.5], [2.0, 1.0], [3.0, 1.0]]
        }
        
        # Pop instruments
        self.instruments = {
            'melody': 0,  # Piano
            'accompaniment': 33  # Electric Bass (finger)
        }
        
        # Pop dynamics - less variation than classical
        self.dynamics = {
            'default': 'mf',
            'variation': 'low'
        }
        
        self.tempo_range = (90, 130)
    
    def get_accompaniment_pattern(self):
        """Return a typical pop accompaniment pattern"""
        return 'eighth'


class RockStyle(PopGenre):
    """Rock music style"""
    
    def __init__(self):
        super().__init__("Rock")
        # Rock-specific chord progressions
        self.chord_progressions = [
            [0, 4, 5, 3],  # I-V-vi-IV
            [0, 3, 0, 4],  # I-IV-I-V (common in rock)
            [0, 0, 3, 3, 0, 0, 4, 4]  # I-I-IV-IV-I-I-V-V (power chord progression)
        ]
        
        # Rock instrumentation
        self.instruments = {
            'melody': 29,  # Electric Guitar (clean)
            'accompaniment': 33  # Electric Bass
        }
        
        # Rock rhythms
        self.rhythm_patterns['rock'] = [[0.0, 0.5], [0.5, 0.5], [1.0, 0.5], [1.5, 0.5],
                                       [2.0, 0.5], [2.5, 0.5], [3.0, 0.5], [3.5, 0.5]]
        
        self.tempo_range = (100, 140)
    
    def get_accompaniment_pattern(self):
        """Return a typical rock accompaniment pattern"""
        return 'rock'


class JazzGenre(GenreBase):
    """Base class for jazz music genres"""
    
    def __init__(self, name="Jazz"):
        super().__init__(name)
        # Common jazz chord progressions
        self.chord_progressions = [
            [1, 4, 0],  # ii-V-I (most common jazz progression)
            [0, 6, 1, 4],  # I-vii-ii-V
            [0, 5, 1, 4, 0]  # I-vi-ii-V-I (turnaround)
        ]
        
        # Jazz rhythms
        self.rhythm_patterns = {
            'swing': [[0.0, 0.66], [0.66, 0.34], [1.0, 0.66], [1.66, 0.34],
                    [2.0, 0.66], [2.66, 0.34], [3.0, 0.66], [3.66, 0.34]],
            'bossa': [[0.0, 0.5], [0.5, 0.5], [1.0, 0.5], [1.5, 0.5],
                     [2.0, 0.5], [2.5, 0.5], [3.0, 0.5], [3.5, 0.5]],
            'walking': [[i, 0.5] for i in [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]]
        }
        
        # Jazz instruments
        self.instruments = {
            'melody': 0,  # Piano
            'accompaniment': 32  # Acoustic Bass
        }
        
        # Jazz uses complex chords
        self.chord_types = {
            'dominant7': [0, 4, 7, 10],
            'major7': [0, 4, 7, 11], 
            'minor7': [0, 3, 7, 10],
            'dimished7': [0, 3, 6, 9],
            'augmented': [0, 4, 8]
        }
        
        self.tempo_range = (80, 140)
    
    def get_accompaniment_pattern(self):
        """Return a typical jazz accompaniment pattern"""
        return 'walking'


class SwingStyle(JazzGenre):
    """Swing jazz style"""
    
    def __init__(self):
        super().__init__("Swing")
        # Swing-specific voicings and rhythms
        self.instruments = {
            'melody': 0,  # Piano
            'accompaniment': 32  # Acoustic Bass
        }
        
        self.tempo_range = (120, 220)
    
    def get_accompaniment_pattern(self):
        """Return a typical swing accompaniment pattern"""
        return 'swing'


class GenreManager:
    """Manages the different genre options and provides access to them"""
    
    def __init__(self):
        self.genres = {}
        self._initialize_genres()
    
    def _initialize_genres(self):
        """Register all available genres"""
        # Classical genres
        self.register_genre('classical', ClassicalGenre())
        self.register_genre('baroque', BaroqueStyle())
        self.register_genre('romantic', RomanticStyle())
        
        # Pop genres
        self.register_genre('pop', PopGenre())
        self.register_genre('rock', RockStyle())
        
        # Jazz genres
        self.register_genre('jazz', JazzGenre())
        self.register_genre('swing', SwingStyle())
    
    def register_genre(self, genre_id, genre_instance):
        """Register a new genre"""
        self.genres[genre_id.lower()] = genre_instance
    
    def get_genre(self, genre_id):
        """Get a genre by ID"""
        return self.genres.get(genre_id.lower(), self.genres.get('classical'))
    
    def get_available_genres(self):
        """Get a list of all available genres"""
        return list(self.genres.keys())
    
    def get_genre_info(self, genre_id):
        """Get information about a specific genre"""
        genre = self.get_genre(genre_id)
        return {
            'name': genre.name,
            'tempo_range': genre.tempo_range,
            'instruments': genre.instruments,
            'chord_progressions': genre.chord_progressions
        }
