"""Test the complete song workflow from selection to MIDI generation."""

import unittest
from pathlib import Path
import sys
import os
import tempfile
import shutil

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.core.song_parser import parse_song_file, normalize_key
from src.core.midi_generator import MIDIGenerator
from src.instruments import Piano, Guitar, Bass, Drums
from src.patterns.pattern_manager import PatternManager
from src.patterns.genre_manager import GenreManager

class TestSongWorkflow(unittest.TestCase):
    """Test the complete song workflow."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.songs_dir = project_root / "input" / "songs"
        self.test_song = self.songs_dir / "Piano_test.txt"
        
        # Create output directory
        self.output_dir = Path(self.temp_dir) / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize managers
        self.pattern_manager = PatternManager()
        self.genre_manager = GenreManager()
    
    def test_key_normalization(self):
        """Test key format normalization."""
        test_cases = [
            ("E minor", "E minor"),
            ("Em", "E minor"),
            ("e minor", "E minor"),
            ("C major", "C major"),
            ("C", "C major"),
            ("F#m", "F minor"),
            ("G", "G major"),
            ("A minor", "A minor")
        ]
        
        for input_key, expected in test_cases:
            self.assertEqual(normalize_key(input_key), expected)
    
    def test_song_selection_and_instrument_generation(self):
        """Test selecting a song and generating appropriate instruments."""
        # Parse the song file
        song_data = parse_song_file(self.test_song)
        
        # Verify song data
        self.assertEqual(song_data.title, "Lament in E Minor")
        self.assertEqual(song_data.tempo, 60)
        self.assertEqual(song_data.time_signature, (4, 4))
        self.assertEqual(song_data.key, "E minor")
        self.assertEqual(song_data.genre, "classical")
        
        # Create MIDI generator with song's tempo and time signature
        midi_gen = MIDIGenerator(
            tempo=song_data.tempo,
            time_signature=song_data.time_signature
        )
        
        # Create instruments based on genre and style
        instruments = []
        
        # Always include piano for this test song
        piano = Piano(midi_channel=0)
        instruments.append(piano)
        
        # Add guitar for accompaniment
        guitar = Guitar(midi_channel=1)
        instruments.append(guitar)
        
        # Add bass for harmony
        bass = Bass(midi_channel=2)
        instruments.append(bass)
        
        # Add drums for rhythm
        drums = Drums(midi_channel=9)
        instruments.append(drums)
        
        # Generate patterns for each instrument
        for instrument in instruments:
            pattern = instrument.generate_pattern(
                chord=song_data.measures[0].chord,
                style=song_data.genre
            )
            self.assertIsNotNone(pattern)
            self.assertGreater(len(pattern), 0)
            
            # Add pattern to MIDI file
            midi_gen.add_pattern(instrument, pattern)
        
        # Write MIDI file
        output_file = self.output_dir / f"{song_data.title.replace(' ', '_')}.mid"
        midi_gen.write(str(output_file))
        
        # Verify MIDI file was created
        self.assertTrue(output_file.exists())
        self.assertGreater(output_file.stat().st_size, 0)
        
        # Cleanup
        midi_gen.cleanup()
        for instrument in instruments:
            instrument.cleanup()
    
    def test_musical_variations(self):
        """Test handling of different musical variations."""
        variation_files = [
            ("test_variations.txt", {
                "title": "Jazz Waltz in F",
                "tempo": 180,
                "time_signature": (3, 4),
                "key": "F major",
                "genre": "jazz"
            }),
            ("test_variations_2.txt", {
                "title": "Blues in A",
                "tempo": 120,
                "time_signature": (12, 8),
                "key": "A minor",
                "genre": "blues"
            }),
            ("test_variations_3.txt", {
                "title": "Pop Ballad in D",
                "tempo": 72,
                "time_signature": (6, 8),
                "key": "D major",
                "genre": "pop"
            })
        ]
        
        for filename, expected in variation_files:
            song_data = parse_song_file(self.songs_dir / filename)
            
            # Verify parsed data matches expected values
            self.assertEqual(song_data.title, expected["title"])
            self.assertEqual(song_data.tempo, expected["tempo"])
            self.assertEqual(song_data.time_signature, expected["time_signature"])
            self.assertEqual(song_data.key, expected["key"])
            self.assertEqual(song_data.genre, expected["genre"])
            
            # Verify measure was created with correct chord
            self.assertIsNotNone(song_data.measures)
            self.assertGreater(len(song_data.measures), 0)
            
            # Create MIDI generator and generate output
            midi_gen = MIDIGenerator(
                tempo=song_data.tempo,
                time_signature=song_data.time_signature
            )
            
            # Create and test instruments
            instruments = [
                Piano(midi_channel=0),
                Guitar(midi_channel=1),
                Bass(midi_channel=2),
                Drums(midi_channel=9)
            ]
            
            for instrument in instruments:
                pattern = instrument.generate_pattern(
                    chord=song_data.measures[0].chord,
                    style=song_data.genre
                )
                self.assertIsNotNone(pattern)
                self.assertGreater(len(pattern), 0)
                midi_gen.add_pattern(instrument, pattern)
            
            # Write MIDI file
            output_file = self.output_dir / f"{song_data.title.replace(' ', '_')}.mid"
            midi_gen.write(str(output_file))
            self.assertTrue(output_file.exists())
            self.assertGreater(output_file.stat().st_size, 0)
            
            # Cleanup
            midi_gen.cleanup()
            for instrument in instruments:
                instrument.cleanup()
    
    def test_invalid_inputs(self):
        """Test handling of invalid inputs."""
        # Test invalid tempo
        with self.assertRaises(ValueError):
            parse_song_file(self.songs_dir / "invalid_tempo.txt")
        
        # Test invalid time signature
        with self.assertRaises(ValueError):
            parse_song_file(self.songs_dir / "invalid_time_sig.txt")
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

if __name__ == '__main__':
    unittest.main() 