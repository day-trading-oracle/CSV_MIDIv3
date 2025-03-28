class Genre:
    """Represents a musical genre with its characteristics"""
    def __init__(self, instrument, style):
        self.instrument = instrument
        self.style = style
    
    def get_instrument(self):
        return self.instrument

class GenreManager:
    """Manages different musical genres and their characteristics"""
    def __init__(self):
        self.genres = {
            'classical': Genre(32, 'basic'),  # Acoustic Bass
            'pop': Genre(33, 'basic'),       # Electric Bass
            'jazz': Genre(34, 'basic')       # Electric Bass (fingered)
        }
    
    def get_genre(self, genre_id):
        """Get genre settings by ID"""
        return self.genres.get(genre_id)

class AccompanimentGenerator:
    """Generates accompaniment patterns based on melody notes"""
    def __init__(self):
        self.genre_manager = GenreManager()
    
    def generate_accompaniment(self, song_data, style='basic', genre_id='classical'):
        """Generate accompaniment for the given song data"""
        # Get genre settings
        genre = self.genre_manager.get_genre(genre_id)
        if not genre:
            genre = self.genre_manager.get_genre('classical')  # Default to classical
        
        # Create basic accompaniment (root notes of chords)
        accompaniment = []
        
        # For each measure in the melody
        for measure in song_data['measures']:
            measure_notes = []
            
            # Find the root note of the measure (simplified)
            root_note = 48  # Default to C3
            
            # Add root note at the start of the measure
            measure_notes.append({
                'pitch': root_note,
                'duration': 1.0,  # Quarter note
                'start': 0,
                'velocity': 70  # Slightly softer than melody
            })
            
            # Add root note at the middle of the measure
            measure_notes.append({
                'pitch': root_note,
                'duration': 1.0,
                'start': 2,
                'velocity': 70
            })
            
            accompaniment.append(measure_notes)
        
        return accompaniment 