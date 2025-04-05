"""
Interactive test script for MusicMidi instruments.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.py_files import Piano, Guitar, Bass, Drums
from src.py_files.midi_generator import MIDIGenerator

def get_genre_choice():
    """Get genre choice from user."""
    print("\nSelect a genre:")
    print("1. Rock")
    print("2. Jazz")
    print("3. Classical")
    print("4. Pop")
    while True:
        try:
            choice = int(input("Enter your choice (1-4): "))
            if 1 <= choice <= 4:
                genres = ['rock', 'jazz', 'classical', 'pop']
                return genres[choice - 1]
            print("Please enter a number between 1 and 4.")
        except ValueError:
            print("Please enter a valid number.")

def get_instrument_style(instrument_name):
    """Get style choice for an instrument from user."""
    print(f"\nSelect style for {instrument_name}:")
    print("1. Simple")
    print("2. Moderate")
    print("3. Complex")
    while True:
        try:
            choice = int(input("Enter your choice (1-3): "))
            if 1 <= choice <= 3:
                styles = ['simple', 'moderate', 'complex']
                return styles[choice - 1]
            print("Please enter a number between 1 and 3.")
        except ValueError:
            print("Please enter a valid number.")

def create_test_song_data(genre):
    """Create a test song with the selected genre."""
    return {
        'title': 'Interactive Test Song',
        'key': 'C',
        'time_signature': '4/4',
        'tempo': 120,
        'genre': genre,
        'measures': [
            {
                'chords': [
                    {'root': 60, 'type': 'major', 'duration': 1.0, 'start': 0.0},
                    {'root': 64, 'type': 'major', 'duration': 1.0, 'start': 1.0},
                    {'root': 67, 'type': 'major', 'duration': 1.0, 'start': 2.0},
                    {'root': 71, 'type': 'major', 'duration': 1.0, 'start': 3.0}
                ]
            },
            {
                'chords': [
                    {'root': 60, 'type': 'major', 'duration': 1.0, 'start': 0.0},
                    {'root': 64, 'type': 'major', 'duration': 1.0, 'start': 1.0},
                    {'root': 67, 'type': 'major', 'duration': 1.0, 'start': 2.0},
                    {'root': 71, 'type': 'major', 'duration': 1.0, 'start': 3.0}
                ]
            }
        ]
    }

def test_instrument(instrument, song_data, output_file):
    """Test a single instrument by generating a pattern and MIDI file."""
    print(f"\nTesting {instrument.__class__.__name__}...")
    
    # Generate pattern
    pattern = instrument.generate_pattern(song_data, is_new_song=True)
    print(f"Generated {len(pattern)} notes")
    
    # Create MIDI file
    generator = MIDIGenerator()
    generator.add_track(instrument.program, pattern)
    
    # Save to file
    output_dir = project_root / 'output'
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / output_file
    generator.save(str(output_path))
    print(f"Saved MIDI file to {output_path}")

def main():
    """Main interactive test function."""
    print("Welcome to MusicMidi Interactive Test!")
    
    # Get genre choice
    genre = get_genre_choice()
    print(f"\nSelected genre: {genre}")
    
    # Create test song data
    song_data = create_test_song_data(genre)
    
    # Initialize instruments
    piano = Piano()
    guitar = Guitar()
    bass = Bass()
    drums = Drums()
    
    # Get style choices for each instrument
    piano.style = get_instrument_style("Piano")
    guitar.style = get_instrument_style("Guitar")
    bass.style = get_instrument_style("Bass")
    drums.style = get_instrument_style("Drums")
    
    # Test each instrument
    test_instrument(piano, song_data, 'interactive_piano.mid')
    test_instrument(guitar, song_data, 'interactive_guitar.mid')
    test_instrument(bass, song_data, 'interactive_bass.mid')
    test_instrument(drums, song_data, 'interactive_drums.mid')
    
    print("\nAll tests completed!")

if __name__ == '__main__':
    main() 