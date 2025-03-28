# MusicMidi

A simple text-to-MIDI converter that transforms human-readable music notation into playable MIDI files.

## Features

- Convert readable music notation to MIDI files
- Simple text format for defining notes, durations, and measures
- Support for multiple voices, chords, and rests
- Automatic accompaniment generation based on melody
- Genre-based music generation with different musical styles

## Input Format

The input format is a simple text file with the following structure:

```
Title: Song Title
Tempo: 120
Time Signature: 4/4
Key: C major

# Comments are supported with the hash symbol
| C4q D4q E4q F4q | G4h A4h | G4w |
```

Notes are specified with:
- Pitch (C, D, E, F, G, A, B, with optional # or b for sharps/flats)
- Octave (0-9)
- Duration (w = whole, h = half, q = quarter, e = eighth, s = sixteenth)
- Optional dot (.) for dotted notes

For full details, see the example songs in the `input/songs` directory.

## Installation

1. Clone the repository:
```
git clone https://github.com/day-trading-oracle/MusicMidi.git
cd MusicMidi
```

2. Install the required dependencies:
```
pip install -r requirements.txt
```

3. Run the setup script to create necessary directories:
```
# On Windows
python setup.ps1

# On Linux/Mac
python setup.py
```

## Usage

### Basic Usage

```
python midi_generator.py input/songs/your_song.txt -o output/your_song.mid
```

### Command Line Options

```
python midi_generator.py input/songs/your_song.txt [-o OUTPUT] [-a ACCOMPANIMENT] [-g GENRE]
```

Arguments:
- `input_file`: Path to the input text file
- `-o, --output`: Output MIDI file name (optional)
- `-a, --accompaniment`: Accompaniment style to generate (optional)
  - Choices: none, basic, quarter, half, whole, waltz, alberti, arpeggio, genre
  - Default: basic
- `-g, --genre`: Musical genre for the accompaniment (optional)
  - Choices: classical, baroque, romantic, pop, rock, jazz, swing

### Genre Selection

You can specify a musical genre to give your accompaniment a specific style:

```
python midi_generator.py input/songs/your_song.txt -a genre -g jazz
```

Available genres:
- classical: Traditional classical music style
- baroque: Baroque music with structured patterns
- romantic: Expressive romantic era style
- pop: Modern pop music style
- rock: Rock music with strong beats
- jazz: Jazz style with complex harmonies
- swing: Swing jazz with characteristic rhythm

### Test Scripts

You can run test scripts to see examples of different features:

```
# Test accompaniment generation
python test_accompaniment.py

# Test genre selection
python test_genre.py
```

## Project Structure

```
MusicMidi/
├── input/                # Directory for input files
│   └── songs/            # Song text files
├── output/               # Generated MIDI files
├── midi_generator.py     # Main script
├── genre_manager.py      # Genre selection system
├── test_accompaniment.py # Test script for accompaniment
├── test_genre.py         # Test script for genre selection
├── setup.ps1             # Setup script for Windows
├── setup.py              # Setup script for Linux/Mac
├── requirements.txt      # Required Python packages
└── README.md             # This file
```

## Contributing

Contributions are welcome! If you'd like to contribute, please:

1. Fork the repository
2. Create a new branch for your feature
3. Add your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 