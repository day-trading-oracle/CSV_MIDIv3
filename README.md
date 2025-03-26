# MusicMidi

A Python-based MIDI file generator that converts text-based musical notation into MIDI files.

## Features

- Convert text-based musical notation to MIDI files
- Support for single notes and chords
- Dynamic control (pp, p, mp, mf, f, ff)
- Multiple duration types (whole, half, quarter, eighth, etc.)
- Precise note timing within measures
- Support for multiple measures (up to 1000)
- Automatic versioning of output files

## Input Format

The input file should follow this format:

```
Title: Song Title
Key: Key Signature
Time Signature: 4/4
Tempo: 120

Measure X Y.Z Note Dynamic Duration
```

Where:
- X is the measure number (1-1000)
- Y.Z is the start time in beats (e.g., 1.0 = beat 1, 1.5 = halfway through beat 1)
- Note is either a single note (e.g., C5) or a chord (e.g., [C5, E5, G5])
- Dynamic is the volume (p, mp, mf, f, etc.)
- Duration is the note length (quarter, half, whole, etc.)

Example:
```
Measure 1 1.0 C5 p quarter
Measure 1 2.0 D5 mf quarter
Measure 1 1.0 [C4, E4, G4] p half
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/MusicMidi.git
cd MusicMidi
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Place your song files in the `input/songs` directory
2. Run the script:
```bash
python midi_generator.py
```
3. Choose to convert a specific song or all songs
4. Find the generated MIDI files in the `output` directory

## Project Structure

```
MusicMidi/
├── input/
│   ├── songs/         # Place your song files here
│   └── templates/     # Template files for new songs
├── output/           # Generated MIDI files
├── midi_generator.py # Main script
├── requirements.txt  # Python dependencies
└── README.md        # This file
```

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 