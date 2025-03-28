#!/usr/bin/env python3
"""
Test script for genre selection feature
This script demonstrates how to generate MIDI files with different genre styles
"""

import os
from pathlib import Path
import midi_generator
from genre_manager import GenreManager

def main():
    """Generate test MIDI files with different genres"""
    # Set up paths with absolute paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base_dir, 'input', 'songs')
    output_dir = os.path.join(base_dir, 'output')
    
    # Create directories if they don't exist
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Get the list of available genres
    genre_manager = GenreManager()
    available_genres = genre_manager.list_genres()
    
    print("Available genres:")
    for genre in available_genres:
        print(f"- {genre}")
    
    # Look for test song file
    test_file = os.path.join(input_dir, 'test_song.txt')
    
    if not os.path.exists(test_file):
        print(f"Test song file not found at {test_file}")
        print("Creating a simple test song file...")
        
        # Create test song file if it doesn't exist
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        with open(test_file, 'w') as f:
            f.write("""Title: Genre Test Song
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
    
    # Generate a MIDI file for each available genre
    for genre in available_genres:
        print(f"\nGenerating MIDI with {genre} genre...")
        
        # Generate the file using genre-specific settings
        output_file = midi_generator.generate_midi(
            song_data,
            accompaniment_style='genre',  # Use genre-specific patterns
            genre=genre
        )
        
        print(f"Generated: {output_file}")
    
    # Also generate a file with each accompaniment style with classical genre
    styles = ['basic', 'quarter', 'half', 'whole', 'waltz', 'alberti', 'arpeggio']
    for style in styles:
        print(f"\nGenerating MIDI with classical genre and {style} accompaniment style...")
        
        # Generate the file
        output_file = midi_generator.generate_midi(
            song_data,
            accompaniment_style=style,
            genre='classical'
        )
        
        print(f"Generated: {output_file}")
    
    print("\nAll test files generated successfully!")
    print(f"MIDI files are available in the {output_dir} directory")

if __name__ == "__main__":
    main() 