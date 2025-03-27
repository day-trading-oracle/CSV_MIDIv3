#!/usr/bin/env python3
"""
Setup script for MusicMidi
Creates necessary directories and sets up the environment for Linux/Mac systems
"""
import os
from pathlib import Path

def main():
    """Create necessary directories and setup the environment"""
    # Get the base directory (where this script is located)
    base_dir = Path(__file__).parent
    
    print("Setting up MusicMidi environment...")
    
    # Create input directory structure
    input_dir = base_dir / 'input'
    songs_dir = input_dir / 'songs'
    
    os.makedirs(songs_dir, exist_ok=True)
    print(f"Created directory: {songs_dir}")
    
    # Create output directory
    output_dir = base_dir / 'output'
    os.makedirs(output_dir, exist_ok=True)
    print(f"Created directory: {output_dir}")
    
    # Check if example songs exist, if not create one
    example_file = songs_dir / 'example_song.txt'
    if not example_file.exists():
        with open(example_file, 'w') as f:
            f.write("""Title: Example Song
Tempo: 120
Time Signature: 4/4
Key: C major

# This is an example song file
# Each line in a measure starts with a pipe symbol (|)
# Notes are specified with pitch (C-B), octave (0-9), and duration (w,h,q,e,s)
# w = whole, h = half, q = quarter, e = eighth, s = sixteenth
# Optionally add . for dotted notes, # for sharps, b for flats

| C4q D4q E4q F4q | G4h A4h | G4w |
| C4q E4q G4q C5q | B4q A4q G4h | F4q D4q F4q A4q | G4w |
""")
        print(f"Created example song file: {example_file}")
    
    # Check if venv exists, suggest creating one if not
    venv_dir = base_dir / '.venv'
    if not venv_dir.exists():
        print("\nVirtual environment not found.")
        print("It's recommended to create a virtual environment:")
        print("python -m venv .venv")
        print("source .venv/bin/activate  # On Linux/Mac")
        print("pip install -r requirements.txt")
    
    print("\nSetup complete!")
    print("\nTo generate MIDI files, run:")
    print("python midi_generator.py input/songs/example_song.txt")
    print("\nOr try the genre selection feature:")
    print("python test_genre.py")

if __name__ == "__main__":
    main() 