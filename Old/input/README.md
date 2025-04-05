# MIDI Input Template System

This directory contains the MIDI input template system for the MusicMidi project. The system provides a comprehensive way to define MIDI music with detailed annotations and parameters.

## Template Structure

The input template system uses a YAML-like format with the following main sections:

### 1. Song Metadata
- `title`: Song title
- `composer`: Composer name
- `genre`: Musical genre
- `tempo`: Base tempo in BPM
- `key`: Musical key
- `time_signature`: Base time signature

### 2. Global MIDI Settings
- `midi_control_changes`: Global MIDI control changes
  - Volume (CC 7)
  - Pan (CC 10)
  - Other MIDI controllers

### 3. Instrument Tracks
Each instrument has its own section with specific parameters:

#### Piano Track
- `program`: MIDI program number
- `channel`: MIDI channel
- `notes`: List of notes with:
  - Pitch
  - Start time
  - Duration
  - Velocity
  - Articulation
  - Dynamic marking
  - Pedal information

#### Guitar Track
- `program`: MIDI program number
- `channel`: MIDI channel
- `chords`: List of chords with:
  - Root note
  - Chord type
  - Start time
  - Duration
  - Velocity
  - Strum pattern
  - Picking technique

#### Bass Track
- `program`: MIDI program number
- `channel`: MIDI channel
- `notes`: List of notes with:
  - Pitch
  - Start time
  - Duration
  - Velocity
  - Articulation
  - Dynamic marking

#### Drums Track
- `program`: MIDI program number (128 for Standard Kit)
- `channel`: MIDI channel (9 for Channel 10)
- `beats`: List of beats with:
  - Position
  - Start time
  - Instruments (kick, snare, hi-hat, etc.)
  - Velocity
  - Technique

### 4. Musical Changes
- `time_signature_changes`: Changes in time signature
- `tempo_changes`: Changes in tempo
- `key_changes`: Changes in key
- `dynamic_changes`: Changes in dynamics
- `articulation_changes`: Changes in articulation

### 5. Advanced MIDI Features
- `control_changes`: MIDI control changes
- `pitch_bend`: Pitch bend events
- `aftertouch`: Aftertouch events

## Usage

1. Create a new input file using the template:
   ```bash
   cp template_song.txt my_song.txt
   ```

2. Edit the file with your musical content:
   - Replace the metadata
   - Add your notes and chords
   - Set appropriate MIDI parameters
   - Add musical changes as needed

3. Validate the input file:
   ```bash
   python -m src.utils.validate_input my_song.txt
   ```

4. Use the file with the MIDI generator:
   ```bash
   python test_midi.py --input my_song.txt
   ```

## Validation Rules

The input system validates:
- Required fields are present
- Note pitches are within instrument ranges
- Velocities are within valid ranges (0-127)
- Durations are positive numbers
- Time signatures are valid
- MIDI channels are unique
- Control change values are valid

## Examples

See the following files for examples:
- `template_song.txt`: Complete template with all features
- `simple_song.txt`: Basic example with minimal parameters
- `complex_song.txt`: Advanced example with all MIDI features

## Error Handling

The system provides detailed error messages for:
- Missing required fields
- Invalid parameter values
- Range violations
- Format errors
- MIDI specification violations

## Future Enhancements

See `future_features.md` for planned improvements to the input template system. 