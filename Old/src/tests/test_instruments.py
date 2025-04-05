"""
Test script for MusicMidi instruments.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.py_files import Piano, Guitar, Bass, Drums
from src.py_files.midi_generator import MIDIGenerator

def create_test_song_data():
    """Create a simple test song with basic chord progression."""
    return {
        'title': 'Test Song',
        'key': 'C',
        'time_signature': '4/4',
        'tempo': 120,
        'genre': 'rock',
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
    """Main test function."""
    print("Starting MusicMidi instrument tests...")
    
    # Create test song data
    song_data = create_test_song_data()
    
    # Initialize instruments
    piano = Piano()
    guitar = Guitar()
    bass = Bass()
    drums = Drums()
    
    # Test each instrument
    test_instrument(piano, song_data, 'test_piano.mid')
    test_instrument(guitar, song_data, 'test_guitar.mid')
    test_instrument(bass, song_data, 'test_bass.mid')
    test_instrument(drums, song_data, 'test_drums.mid')
    
    print("\nAll tests completed!")

if __name__ == '__main__':
    main() 