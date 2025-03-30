"""
Test suite for bass instrument functionality.
Tests various bass patterns and note ranges.
"""

import unittest
from src.instruments.bass import Bass
from src.midi_generator import generate_midi

class TestBass(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.bass = Bass()
        self.test_song_data = {
            'title': 'Test Bass Song',
            'key': 'C',
            'time_signature': '4/4',
            'tempo': 120,
            'measures': []
        }

    def test_walking_bass_pattern(self):
        """Test walking bass pattern generation"""
        pattern = self.bass.generate_pattern(self.test_song_data, 'walking')
        self.assertIsNotNone(pattern)
        self.assertTrue(len(pattern) > 0)
        
        # Test note range
        for note in pattern:
            if isinstance(note, list):  # Handle chords
                for n in note:
                    self.assertTrue(28 <= n['pitch'] <= 55)  # Bass range
            else:
                self.assertTrue(28 <= note['pitch'] <= 55)

    def test_rock_bass_pattern(self):
        """Test rock bass pattern generation"""
        pattern = self.bass.generate_pattern(self.test_song_data, 'rock')
        self.assertIsNotNone(pattern)
        self.assertTrue(len(pattern) > 0)
        
        # Test note range and rhythm
        for note in pattern:
            if isinstance(note, list):
                for n in note:
                    self.assertTrue(28 <= n['pitch'] <= 55)
                    self.assertTrue(n['duration'] >= 0.5)  # Rock typically uses quarter notes or longer
            else:
                self.assertTrue(28 <= note['pitch'] <= 55)
                self.assertTrue(note['duration'] >= 0.5)

    def test_funk_bass_pattern(self):
        """Test funk bass pattern generation."""
        bass = Bass()
        chord = [60]  # C4
        duration = 4.0  # 4/4 measure
        pattern = bass._create_funk_pattern(chord, duration)
        
        self.assertEqual(len(pattern), 4)
        for note in pattern:
            self.assertGreaterEqual(note.pitch, 60)
            self.assertLessEqual(note.pitch, 67)  # C4 to G4
            self.assertEqual(note.duration, 1.0)  # Quarter note duration
            self.assertGreaterEqual(note.velocity, 85)
            self.assertLessEqual(note.velocity, 105)

    def test_jazz_bass_pattern(self):
        """Test jazz bass pattern generation."""
        bass = Bass()
        chord = [60, 64, 67]  # C4, E4, G4
        duration = 4.0  # 4/4 measure
        pattern = bass._create_jazz_pattern(chord, duration)
        
        self.assertEqual(len(pattern), 4)
        for note in pattern:
            self.assertGreaterEqual(note.pitch, 60)
            self.assertLessEqual(note.pitch, 67)  # C4 to G4
            self.assertEqual(note.duration, 1.0)  # Quarter note duration
            self.assertGreaterEqual(note.velocity, 80)
            self.assertLessEqual(note.velocity, 90)

    def test_pop_bass_pattern(self):
        """Test pop bass pattern generation"""
        pattern = self.bass.generate_pattern(self.test_song_data, 'pop')
        self.assertIsNotNone(pattern)
        self.assertTrue(len(pattern) > 0)
        
        # Test note range and rhythm
        for note in pattern:
            if isinstance(note, list):
                for n in note:
                    self.assertTrue(28 <= n['pitch'] <= 55)
                    self.assertTrue(n['duration'] >= 0.5)  # Pop typically uses quarter notes or longer
            else:
                self.assertTrue(28 <= note['pitch'] <= 55)
                self.assertTrue(note['duration'] >= 0.5)

    def test_invalid_pattern(self):
        """Test handling of invalid pattern type"""
        with self.assertRaises(ValueError):
            self.bass.generate_pattern(self.test_song_data, 'invalid_style')

    def test_empty_song_data(self):
        """Test handling of empty song data"""
        empty_song = {
            'title': 'Empty Song',
            'key': 'C',
            'time_signature': '4/4',
            'tempo': 120,
            'measures': []
        }
        pattern = self.bass.generate_pattern(empty_song, 'walking')
        self.assertIsNotNone(pattern)
        self.assertTrue(len(pattern) > 0)

    def test_chord_progressions(self):
        """Test chord progression generation"""
        # Test classical progression
        prog = self.bass.get_chord_progression('classical')
        self.assertIsNotNone(prog)
        self.assertTrue(len(prog) > 0)
        
        # Test jazz progression
        prog = self.bass.get_chord_progression('jazz')
        self.assertIsNotNone(prog)
        self.assertTrue(len(prog) > 0)
        
        # Test pop progression
        prog = self.bass.get_chord_progression('pop')
        self.assertIsNotNone(prog)
        self.assertTrue(len(prog) > 0)

    def test_time_signature_conversion(self):
        """Test conversion of different time signatures to 4/4"""
        # Test 3/4 to 4/4 conversion
        duration = self.bass.convert_to_4_4(3.0, '3/4')
        self.assertAlmostEqual(duration, 4.0, places=2)
        
        # Test 6/8 to 4/4 conversion
        duration = self.bass.convert_to_4_4(6.0, '6/8')
        self.assertAlmostEqual(duration, 4.0, places=2)
        
        # Test 5/4 to 4/4 conversion
        duration = self.bass.convert_to_4_4(5.0, '5/4')
        self.assertAlmostEqual(duration, 4.0, places=2)
        
        # Test unknown time signature (should return original duration)
        duration = self.bass.convert_to_4_4(3.0, 'unknown')
        self.assertEqual(duration, 3.0)

    def test_pattern_with_different_time_signatures(self):
        """Test pattern generation with different time signatures"""
        # Test 3/4 time
        song_data_3_4 = {
            'title': 'Test 3/4 Song',
            'key': 'C',
            'time_signature': '3/4',
            'tempo': 120,
            'measures': [{'chord': [60, 64, 67]}]
        }
        pattern_3_4 = self.bass.generate_pattern(song_data_3_4, 'walking')
        self.assertTrue(len(pattern_3_4) > 0)
        self.assertEqual(pattern_3_4[0]['original_time_sig'], '3/4')
        
        # Test 6/8 time
        song_data_6_8 = {
            'title': 'Test 6/8 Song',
            'key': 'C',
            'time_signature': '6/8',
            'tempo': 120,
            'measures': [{'chord': [60, 64, 67]}]
        }
        pattern_6_8 = self.bass.generate_pattern(song_data_6_8, 'walking')
        self.assertTrue(len(pattern_6_8) > 0)
        self.assertEqual(pattern_6_8[0]['original_time_sig'], '6/8')

    def test_pattern_duration_conversion(self):
        """Test that pattern durations are properly converted"""
        song_data = {
            'title': 'Test Conversion',
            'key': 'C',
            'time_signature': '3/4',
            'tempo': 120,
            'measures': [{'chord': [60, 64, 67]}]
        }
        
        # Test walking pattern in 3/4
        pattern = self.bass.generate_pattern(song_data, 'walking')
        
        # Check that all notes are within the converted measure duration
        for note in pattern:
            self.assertLessEqual(
                note['start'] + note['duration'],
                self.bass.convert_to_4_4(4.0, '3/4'),
                "Note should not extend beyond converted measure duration"
            )
            
        # Check that the pattern preserves relative timing
        if len(pattern) > 1:
            for i in range(len(pattern) - 1):
                self.assertLess(
                    pattern[i]['start'],
                    pattern[i + 1]['start'],
                    "Notes should be in sequential order"
                )
                
        # Verify original time signature is preserved
        for note in pattern:
            self.assertEqual(note['original_time_sig'], '3/4')

if __name__ == '__main__':
    unittest.main() 