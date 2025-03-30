"""
Comprehensive test suite for all instruments.
Tests each instrument with different genres, styles, and time signatures.
"""

import unittest
from src.instruments.piano import Piano
from src.instruments.guitar import Guitar
from src.instruments.bass import Bass
from src.instruments.drums import Drums

class TestInstruments(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.piano = Piano()
        self.guitar = Guitar()
        self.bass = Bass()
        self.drums = Drums()
        
        # Test data for different genres and styles
        self.test_data = {
            'classical': {
                'time_signature': '4/4',
                'tempo': 120,
                'key': 'C',
                'measures': [
                    {
                        'chord': [60, 64, 67],  # C major
                        'melody': [
                            {'pitch': 60, 'duration': 1.0, 'start': 0.0, 'velocity': 80},
                            {'pitch': 64, 'duration': 1.0, 'start': 1.0, 'velocity': 75}
                        ],
                        'chords': [
                            {'root': 60, 'type': 'major', 'duration': 2.0, 'start': 0.0},
                            {'root': 64, 'type': 'minor', 'duration': 2.0, 'start': 2.0}
                        ],
                        'beats': [
                            {'position': 0, 'start': 0.0},
                            {'position': 1, 'start': 0.5}
                        ]
                    }
                ]
            },
            'jazz': {
                'time_signature': '4/4',
                'tempo': 140,
                'key': 'G',
                'measures': [
                    {
                        'chord': [67, 71, 74],  # G major
                        'melody': [
                            {'pitch': 67, 'duration': 0.5, 'start': 0.0, 'velocity': 90},
                            {'pitch': 71, 'duration': 0.5, 'start': 0.5, 'velocity': 85}
                        ],
                        'chords': [
                            {'root': 67, 'type': 'major', 'duration': 1.0, 'start': 0.0},
                            {'root': 71, 'type': 'minor', 'duration': 1.0, 'start': 1.0}
                        ],
                        'beats': [
                            {'position': 0, 'start': 0.0},
                            {'position': 1, 'start': 0.5}
                        ]
                    }
                ]
            },
            'rock': {
                'time_signature': '4/4',
                'tempo': 160,
                'key': 'E',
                'measures': [
                    {
                        'chord': [64, 67, 71],  # E major
                        'melody': [
                            {'pitch': 64, 'duration': 0.25, 'start': 0.0, 'velocity': 100},
                            {'pitch': 67, 'duration': 0.25, 'start': 0.25, 'velocity': 95}
                        ],
                        'chords': [
                            {'root': 64, 'type': 'major', 'duration': 1.0, 'start': 0.0},
                            {'root': 67, 'type': 'major', 'duration': 1.0, 'start': 1.0}
                        ],
                        'beats': [
                            {'position': 0, 'start': 0.0},
                            {'position': 1, 'start': 0.5}
                        ]
                    }
                ]
            }
        }
        
        # Test data for different time signatures
        self.time_sig_data = {
            '3/4': {
                'time_signature': '3/4',
                'tempo': 120,
                'key': 'C',
                'measures': [
                    {
                        'chord': [60, 64, 67],  # C major
                        'melody': [
                            {'pitch': 60, 'duration': 1.0, 'start': 0.0, 'velocity': 80},
                            {'pitch': 64, 'duration': 1.0, 'start': 1.0, 'velocity': 75},
                            {'pitch': 67, 'duration': 1.0, 'start': 2.0, 'velocity': 70}
                        ]
                    }
                ]
            },
            '6/8': {
                'time_signature': '6/8',
                'tempo': 120,
                'key': 'C',
                'measures': [
                    {
                        'chord': [60, 64, 67],  # C major
                        'melody': [
                            {'pitch': 60, 'duration': 0.5, 'start': 0.0, 'velocity': 80},
                            {'pitch': 64, 'duration': 0.5, 'start': 0.5, 'velocity': 75},
                            {'pitch': 67, 'duration': 0.5, 'start': 1.0, 'velocity': 70}
                        ]
                    }
                ]
            }
        }

    def test_piano_with_genres(self):
        """Test piano with different genres"""
        for genre, data in self.test_data.items():
            pattern = self.piano.generate_pattern(data, genre=genre)
            self.assertIsNotNone(pattern)
            self.assertTrue(len(pattern) > 0)
            
            # Check note properties
            for note in pattern:
                self.assertIn('pitch', note)
                self.assertIn('duration', note)
                self.assertIn('start', note)
                self.assertIn('velocity', note)
                self.assertIn('original_time_sig', note)
                
                # Check ranges
                self.assertTrue(21 <= note['pitch'] <= 108)  # Piano range
                self.assertTrue(30 <= note['velocity'] <= 120)
                self.assertEqual(note['original_time_sig'], data['time_signature'])

    def test_guitar_with_genres(self):
        """Test guitar with different genres"""
        for genre, data in self.test_data.items():
            pattern = self.guitar.generate_pattern(data, genre=genre)
            self.assertIsNotNone(pattern)
            self.assertTrue(len(pattern) > 0)
            
            # Check note properties
            for note in pattern:
                self.assertIn('pitch', note)
                self.assertIn('duration', note)
                self.assertIn('start', note)
                self.assertIn('velocity', note)
                self.assertIn('original_time_sig', note)
                
                # Check ranges
                self.assertTrue(40 <= note['pitch'] <= 76)  # Guitar range
                self.assertTrue(30 <= note['velocity'] <= 120)
                self.assertEqual(note['original_time_sig'], data['time_signature'])

    def test_bass_with_genres(self):
        """Test bass with different genres"""
        for genre, data in self.test_data.items():
            pattern = self.bass.generate_pattern(data, genre=genre)
            self.assertIsNotNone(pattern)
            self.assertTrue(len(pattern) > 0)
            
            # Check note properties
            for note in pattern:
                self.assertIn('pitch', note)
                self.assertIn('duration', note)
                self.assertIn('start', note)
                self.assertIn('velocity', note)
                self.assertIn('original_time_sig', note)
                
                # Check ranges
                self.assertTrue(24 <= note['pitch'] <= 55)  # Bass range
                self.assertTrue(30 <= note['velocity'] <= 120)
                self.assertEqual(note['original_time_sig'], data['time_signature'])

    def test_drums_with_genres(self):
        """Test drums with different genres"""
        for genre, data in self.test_data.items():
            pattern = self.drums.generate_pattern(data, genre=genre)
            self.assertIsNotNone(pattern)
            self.assertTrue(len(pattern) > 0)
            
            # Check note properties
            for note in pattern:
                self.assertIn('pitch', note)
                self.assertIn('duration', note)
                self.assertIn('start', note)
                self.assertIn('velocity', note)
                self.assertIn('original_time_sig', note)
                
                # Check ranges
                self.assertTrue(35 <= note['pitch'] <= 81)  # Drums range
                self.assertTrue(30 <= note['velocity'] <= 120)
                self.assertEqual(note['original_time_sig'], data['time_signature'])

    def test_instruments_with_time_signatures(self):
        """Test all instruments with different time signatures"""
        instruments = [self.piano, self.guitar, self.bass, self.drums]
        
        for time_sig, data in self.time_sig_data.items():
            for instrument in instruments:
                pattern = instrument.generate_pattern(data)
                self.assertIsNotNone(pattern)
                self.assertTrue(len(pattern) > 0)
                
                # Check time signature conversion
                for note in pattern:
                    self.assertEqual(note['original_time_sig'], time_sig)
                    
                    # Verify timing is properly converted
                    if time_sig == '3/4':
                        self.assertLessEqual(note['start'] + note['duration'], 4.0)
                    elif time_sig == '6/8':
                        self.assertLessEqual(note['start'] + note['duration'], 4.0)

    def test_instrument_ranges(self):
        """Test that all instruments respect their playable ranges"""
        instruments = [
            (self.piano, 21, 108),  # Piano range
            (self.guitar, 40, 76),  # Guitar range
            (self.bass, 24, 55),    # Bass range
            (self.drums, 35, 81)    # Drums range
        ]
        
        for instrument, min_pitch, max_pitch in instruments:
            pattern = instrument.generate_pattern(self.test_data['classical'])
            
            for note in pattern:
                self.assertTrue(min_pitch <= note['pitch'] <= max_pitch,
                              f"Note pitch {note['pitch']} outside range for {instrument.__class__.__name__}")

    def test_velocity_ranges(self):
        """Test that all instruments respect velocity ranges"""
        instruments = [self.piano, self.guitar, self.bass, self.drums]
        
        for instrument in instruments:
            pattern = instrument.generate_pattern(self.test_data['classical'])
            
            for note in pattern:
                self.assertTrue(30 <= note['velocity'] <= 120,
                              f"Velocity {note['velocity']} outside range for {instrument.__class__.__name__}")

    def test_drum_midi_mappings(self):
        """Test that drum MIDI note mappings are correct"""
        # Create a simple test data with just one measure
        test_data = {
            'time_signature': '4/4',
            'tempo': 120,
            'key': 'C',
            'measures': [
                {
                    'beats': [
                        {'position': 0, 'start': 0.0},
                        {'position': 1, 'start': 1.0},
                        {'position': 2, 'start': 2.0},
                        {'position': 3, 'start': 3.0}
                    ]
                }
            ]
        }
        
        # Generate drum pattern with base rock pattern
        pattern = self.drums.generate_pattern(test_data, genre='rock', variation=0)
        
        # Verify drum mappings
        drum_notes = {
            'kick': 36,    # C1
            'snare': 38,   # D1
            'hihat': 42,   # F#1
            'tom1': 45,    # A1
            'tom2': 47,    # B1
            'crash': 49,   # C#2
            'ride': 51,    # D#2
        }
        
        # Check that kick and snare are present
        kick_notes = [note for note in pattern if note['pitch'] == drum_notes['kick']]
        snare_notes = [note for note in pattern if note['pitch'] == drum_notes['snare']]
        hihat_notes = [note for note in pattern if note['pitch'] == drum_notes['hihat']]
        
        self.assertTrue(len(kick_notes) > 0, "Kick drum notes should be present")
        self.assertTrue(len(snare_notes) > 0, "Snare drum notes should be present")
        self.assertTrue(len(hihat_notes) > 0, "Hi-hat notes should be present")
        
        # Get base pattern configuration
        base_pattern = self.drums.genre_patterns['rock']['base']
        
        # Verify kick drum timing (should be on beats 1 and 3)
        kick_times = [note['start'] for note in kick_notes]
        for beat in base_pattern['kick']:
            self.assertTrue(beat in kick_times, f"Kick should be on beat {beat}")
        
        # Verify snare drum timing (should be on beats 2 and 4)
        snare_times = [note['start'] for note in snare_notes]
        for beat in base_pattern['snare']:
            self.assertTrue(beat in snare_times, f"Snare should be on beat {beat}")
        
        # Verify hi-hat timing (should be on every eighth note)
        hihat_times = [note['start'] for note in hihat_notes]
        expected_hihat_times = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
        for expected_time in expected_hihat_times:
            self.assertTrue(expected_time in hihat_times, f"Hi-hat should be on beat {expected_time}")
        
        # Verify note durations
        for note in pattern:
            if note['pitch'] == drum_notes['kick']:
                self.assertEqual(note['duration'], 0.1, "Kick drum should have short duration")
            elif note['pitch'] == drum_notes['snare']:
                self.assertEqual(note['duration'], 0.1, "Snare drum should have short duration")
            elif note['pitch'] == drum_notes['hihat']:
                self.assertEqual(note['duration'], 0.05, "Hi-hat should have very short duration")
        
        # Verify velocities match base pattern
        for note in pattern:
            if note['pitch'] == drum_notes['kick']:
                self.assertEqual(note['velocity'], base_pattern['velocity']['kick'], "Kick drum velocity should match base pattern")
            elif note['pitch'] == drum_notes['snare']:
                self.assertEqual(note['velocity'], base_pattern['velocity']['snare'], "Snare drum velocity should match base pattern")
            elif note['pitch'] == drum_notes['hihat']:
                self.assertEqual(note['velocity'], base_pattern['velocity']['hihat'], "Hi-hat velocity should match base pattern")

    def test_drum_genre_patterns(self):
        """Test that drum patterns vary by genre"""
        # Test data for different genres
        test_data = {
            'time_signature': '4/4',
            'tempo': 120,
            'key': 'C',
            'measures': [
                {
                    'beats': [
                        {'position': 0, 'start': 0.0},
                        {'position': 1, 'start': 1.0},
                        {'position': 2, 'start': 2.0},
                        {'position': 3, 'start': 3.0}
                    ]
                }
            ]
        }
        
        # Test each genre
        genres = ['rock', 'jazz', 'funk', 'classical']
        for genre in genres:
            pattern = self.drums.generate_pattern(test_data, genre=genre, variation=0)
            
            # Get notes for each drum
            kick_notes = [note for note in pattern if note['pitch'] == self.drums.drum_map['kick']]
            snare_notes = [note for note in pattern if note['pitch'] == self.drums.drum_map['snare']]
            hihat_notes = [note for note in pattern if note['pitch'] == self.drums.drum_map['hihat']]
            
            # Get genre-specific pattern
            genre_pattern = self.drums.genre_patterns[genre]['base']
            
            # Verify kick drum pattern
            kick_times = [note['start'] for note in kick_notes]
            for beat in genre_pattern['kick']:
                self.assertTrue(beat in kick_times, f"Kick should be on beat {beat} for {genre}")
            
            # Verify snare drum pattern
            snare_times = [note['start'] for note in snare_notes]
            for beat in genre_pattern['snare']:
                self.assertTrue(beat in snare_times, f"Snare should be on beat {beat} for {genre}")
            
            # Verify hi-hat pattern
            hihat_times = [note['start'] for note in hihat_notes]
            if genre_pattern['hihat'] == 'eighth':
                expected_hihat_times = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
            elif genre_pattern['hihat'] == 'sixteenth':
                expected_hihat_times = [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25, 3.5, 3.75]
            else:  # quarter
                expected_hihat_times = [0.0, 1.0, 2.0, 3.0]
            
            for expected_time in expected_hihat_times:
                self.assertTrue(expected_time in hihat_times, f"Hi-hat should be on beat {expected_time} for {genre}")
            
            # Verify velocities
            for note in pattern:
                if note['pitch'] == self.drums.drum_map['kick']:
                    self.assertEqual(note['velocity'], genre_pattern['velocity']['kick'], 
                                  f"Kick velocity should be {genre_pattern['velocity']['kick']} for {genre}")
                elif note['pitch'] == self.drums.drum_map['snare']:
                    self.assertEqual(note['velocity'], genre_pattern['velocity']['snare'],
                                  f"Snare velocity should be {genre_pattern['velocity']['snare']} for {genre}")
                elif note['pitch'] == self.drums.drum_map['hihat']:
                    self.assertEqual(note['velocity'], genre_pattern['velocity']['hihat'],
                                  f"Hi-hat velocity should be {genre_pattern['velocity']['hihat']} for {genre}")

    def test_drum_pattern_variations(self):
        """Test that drum patterns can be generated with different variations"""
        # Test data for different genres
        test_data = {
            'time_signature': '4/4',
            'tempo': 120,
            'key': 'C',
            'measures': [
                {
                    'beats': [
                        {'position': 0, 'start': 0.0},
                        {'position': 1, 'start': 1.0},
                        {'position': 2, 'start': 2.0},
                        {'position': 3, 'start': 3.0}
                    ]
                }
            ]
        }
        
        # Test each genre with different variations
        genres = ['rock', 'jazz', 'funk', 'classical']
        for genre in genres:
            # Test base pattern
            base_pattern = self.drums.generate_pattern(test_data, genre=genre, variation=0)
            self.assertIsNotNone(base_pattern)
            self.assertTrue(len(base_pattern) > 0)
            
            # Test specific variations
            for variation in range(2):  # Each genre has 2 variations
                pattern = self.drums.generate_pattern(test_data, genre=genre, variation=variation)
                self.assertIsNotNone(pattern)
                self.assertTrue(len(pattern) > 0)
                
                # Get notes for each drum
                kick_notes = [note for note in pattern if note['pitch'] == self.drums.drum_map['kick']]
                snare_notes = [note for note in pattern if note['pitch'] == self.drums.drum_map['snare']]
                hihat_notes = [note for note in pattern if note['pitch'] == self.drums.drum_map['hihat']]
                
                # Get genre-specific pattern
                genre_data = self.drums.genre_patterns[genre]
                pattern_config = genre_data['variations'][variation]
                
                # Verify kick drum pattern
                kick_times = [note['start'] for note in kick_notes]
                for beat in pattern_config['kick']:
                    self.assertTrue(beat in kick_times, f"Kick should be on beat {beat} for {genre} variation {variation}")
                
                # Verify snare drum pattern
                snare_times = [note['start'] for note in snare_notes]
                for beat in pattern_config['snare']:
                    self.assertTrue(beat in snare_times, f"Snare should be on beat {beat} for {genre} variation {variation}")
                
                # Verify hi-hat pattern
                hihat_times = [note['start'] for note in hihat_notes]
                if pattern_config['hihat'] == 'eighth':
                    expected_hihat_times = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
                elif pattern_config['hihat'] == 'sixteenth':
                    expected_hihat_times = [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.25, 3.5, 3.75]
                else:  # quarter
                    expected_hihat_times = [0.0, 1.0, 2.0, 3.0]
                
                for expected_time in expected_hihat_times:
                    self.assertTrue(expected_time in hihat_times, f"Hi-hat should be on beat {expected_time} for {genre} variation {variation}")
                
                # Verify velocities
                for note in pattern:
                    if note['pitch'] == self.drums.drum_map['kick']:
                        self.assertEqual(note['velocity'], pattern_config['velocity']['kick'], 
                                      f"Kick velocity should be {pattern_config['velocity']['kick']} for {genre} variation {variation}")
                    elif note['pitch'] == self.drums.drum_map['snare']:
                        self.assertEqual(note['velocity'], pattern_config['velocity']['snare'],
                                      f"Snare velocity should be {pattern_config['velocity']['snare']} for {genre} variation {variation}")
                    elif note['pitch'] == self.drums.drum_map['hihat']:
                        self.assertEqual(note['velocity'], pattern_config['velocity']['hihat'],
                                      f"Hi-hat velocity should be {pattern_config['velocity']['hihat']} for {genre} variation {variation}")
            
            # Test random variation
            random_pattern = self.drums.generate_pattern(test_data, genre=genre)
            self.assertIsNotNone(random_pattern)
            self.assertTrue(len(random_pattern) > 0)

if __name__ == '__main__':
    unittest.main() 