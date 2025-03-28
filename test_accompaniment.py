#!/usr/bin/env python3
"""
Test script for accompaniment generator
This script generates different accompaniment patterns for a test song
"""

import os
import midi_generator
from genre_manager import GenreManager

def main():
    """Generate test MIDI files with different accompaniment styles"""
    # Set up paths with absolute paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base_dir, 'input', 'songs')
    output_dir = os.path.join(base_dir, 'output')
    
    # Create directories if they don't exist
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Look for test song file
    test_file = os.path.join(input_dir, 'test_song.txt')
    
    if not os.path.exists(test_file):
        print(f"Test song file not found at {test_file}")
        print("Creating a simple test song file...")
        
        # Create test song file if it doesn't exist
        with open(test_file, 'w') as f:
            f.write("""Title: Accompaniment Test Song
Tempo: 120
Time Signature: 4/4
Key: C major

# A simple melody in C major
| C4q D4q E4q F4q | G4q A4q G4q F4q | E4q D4q C4h |
| C4q E4q G4q C5q | B4q A4q G4h | F4q D4q F4q A4q | G4w |
""")
        print(f"Created test song file at {test_file}")
    
    # Read and parse the test song
    with open(test_file, 'r') as f:
        song_lines = f.readlines()
    
    song_data = midi_generator.parse_song(song_lines)
    
    # Generate a MIDI file for each accompaniment style
    styles = ['none', 'basic', 'quarter', 'half', 'whole', 'waltz', 'alberti', 'arpeggio']
    
    for style in styles:
        print(f"\nGenerating MIDI with {style} accompaniment...")
        
        # Generate the file
        output_file = midi_generator.generate_midi(
            song_data,
            accompaniment_style=style
        )
        
        print(f"Generated: {output_file}")
    
    print("\nAll test files generated successfully!")
    print(f"MIDI files are available in the {output_dir} directory")

if __name__ == "__main__":
    main() 