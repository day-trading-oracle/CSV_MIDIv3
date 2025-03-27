"""
Test script for the automatic accompaniment feature with music theory
This script runs in non-interactive mode to test the enhanced accompaniment features
"""

import os
import sys
from midi_generator import process_song, process_all_songs

def main():
    print("MusicMidi Music Theory Accompaniment Test Script")
    print("===============================================")
    
    # Define directories
    input_dir = os.path.join(os.path.dirname(__file__), 'input', 'songs')
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    
    # Test song (using the test_song_new_format.txt)
    test_song = os.path.join(input_dir, 'test_song_new_format.txt')
    
    if not os.path.exists(test_song):
        print(f"Error: Test song not found at {test_song}")
        return
    
    print("\nTest 1: Converting test song without accompaniment")
    process_song(test_song, output_dir, enable_accompaniment=False)
    
    print("\nTest 2: Converting test song with music theory-based accompaniment (basic style)")
    process_song(test_song, output_dir, enable_accompaniment=True, accompaniment_style='basic')
    
    print("\nTest 3: Converting test song with music theory-based accompaniment (arpeggio style)")
    process_song(test_song, output_dir, enable_accompaniment=True, accompaniment_style='arpeggio')
    
    print("\nTest 4: Converting test song with music theory-based accompaniment (alberti style)")
    process_song(test_song, output_dir, enable_accompaniment=True, accompaniment_style='alberti')
    
    print("\nAll tests completed! Check the output directory for the generated MIDI files.")
    print("\nThe following files should now be available in the output directory:")
    print("1. Test_Song_New_Format_melody_only_C_major_v1.mid - Original melody only")
    print("2. Test_Song_New_Format_basic_accompaniment_C_major_v1.mid - With block chord accompaniment")
    print("3. Test_Song_New_Format_arpeggio_accompaniment_C_major_v1.mid - With arpeggiated accompaniment")
    print("4. Test_Song_New_Format_alberti_accompaniment_C_major_v1.mid - With alberti bass accompaniment")
    
    # Try to list the output directory contents
    try:
        print("\nActual output directory contents:")
        files = os.listdir(output_dir)
        for i, file in enumerate(sorted(files), 1):
            if file.startswith("Test_Song_New_Format") and file.endswith(".mid"):
                print(f"{i}. {file}")
    except Exception as e:
        print(f"Could not list output directory: {e}")

if __name__ == "__main__":
    main() 