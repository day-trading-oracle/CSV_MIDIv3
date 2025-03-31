import os

def test_generate_midi_with_instruments(self):
    """Test generating MIDI with multiple instruments."""
    # Load test song
    song_data = load_song('test_song.txt')
    
    # Initialize instruments
    piano = Piano()
    guitar = Guitar()
    bass = Bass()
    
    # Generate patterns for each instrument
    piano_pattern = piano.generate_pattern(song_data, is_new_song=True)
    guitar_pattern = guitar.generate_pattern(song_data, is_new_song=True)
    bass_pattern = bass.generate_pattern(song_data, is_new_song=True)
    
    # Verify patterns are not empty
    self.assertTrue(len(piano_pattern) > 0, "Piano pattern should not be empty")
    self.assertTrue(len(guitar_pattern) > 0, "Guitar pattern should not be empty")
    self.assertTrue(len(bass_pattern) > 0, "Bass pattern should not be empty")
    
    # Create instrument dictionaries
    instruments = [
        {
            'name': 'Piano',
            'program': piano.program,
            'pattern': piano_pattern
        },
        {
            'name': 'Guitar',
            'program': guitar.program,
            'pattern': guitar_pattern
        },
        {
            'name': 'Bass',
            'program': bass.program,
            'pattern': bass_pattern
        }
    ]
    
    # Generate MIDI file
    output_file = os.path.join(self.output_dir, 'test_output.mid')
    generate_midi(song_data, instruments, output_file)
    
    # Verify output file exists
    self.assertTrue(os.path.exists(output_file), "MIDI file should be generated") 