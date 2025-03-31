from pathlib import Path
import sys
import os

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent
src_path = str(project_root / 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from midiutil import MIDIFile
import math
from datetime import datetime
from typing import List, Dict
import json
from py_files.bass import Bass
from py_files.guitar import Guitar
from py_files.drums import Drums
from py_files.piano import Piano

def parse_note(note_str: str) -> int:
    """Convert a note string (e.g., 'E2' or '60') to MIDI pitch."""
    if not note_str:
        raise ValueError("Empty note string")
        
    # MIDI note mapping
    note_to_midi = {
        'C': 0, 'Cs': 1, 'Db': 1, 'D': 2, 'Ds': 3, 'Eb': 3, 'E': 4, 'F': 5,
        'Fs': 6, 'Gb': 6, 'G': 7, 'Gs': 8, 'Ab': 8, 'A': 9, 'As': 10, 'Bb': 10, 'B': 11
    }
    
    try:
        # Try direct MIDI number first
        return int(note_str)
    except ValueError:
        # Parse note name and octave
        if len(note_str) < 2:
            raise ValueError(f"Invalid note format: {note_str}")
            
        # Get the octave (last character)
        try:
            octave = int(note_str[-1])
        except ValueError:
            raise ValueError(f"Invalid octave in note: {note_str}")
            
        # Get the note name (everything except the last character)
        note = note_str[:-1]
        
        # Handle sharps and flats
        if '#' in note:
            note = note.replace('#', 's')
        elif 'b' in note:
            note = note.replace('b', 'b')
            
        # Validate note name
        if note not in note_to_midi:
            raise ValueError(f"Invalid note name: {note}")
            
        # Get MIDI pitch
        pitch = note_to_midi[note]
        # Add octave offset
        return pitch + (octave + 1) * 12

def load_song_direct(filename: str) -> dict:
    """Load a song directly from the text file."""
    file_path = Path(filename)
    if not file_path.exists():
        raise FileNotFoundError(f"Song file not found: {file_path}")
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Parse song data
    song_data = {
        'title': '',
        'tempo': 120,
        'time_signature': '4/4',
        'genre': 'rock',
        'key': 'C',
        'instruments': {'piano': {}},  # Initialize piano instrument
        'measures': [],     # List to store measures in order
        'sections': [],     # List to store section information
        'emotional_context': {},  # Dictionary to store emotional context
        'performance_notes': []   # List to store performance notes
    }
    
    current_instrument = 'piano'  # Default to piano
    current_measure = None
    current_section = None
    in_notes = False
    
    # Dynamics mapping
    dynamics = {
        'pp': 20, 'p': 40, 'mp': 60, 'mf': 80, 'f': 100, 'ff': 120
    }
    
    # Duration mapping
    durations = {
        'whole': 4.0, 'half': 2.0, 'quarter': 1.0, 'eighth': 0.5, 'sixteenth': 0.25
    }
    
    # Skip format description lines
    header_found = False
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Skip section headers and dividers
        if line.startswith('=') or line.startswith('-') or line == 'MIDI Piano Piece':
            continue
            
        # Skip format description until we find the header information
        if not header_found:
            if line == 'Header Information:':
                header_found = True
            continue
            
        # Skip format description lines
        if (line.startswith('Where:') or 
            line.startswith('Each line') or 
            line.startswith('Format:') or 
            line.startswith('Piece:') or 
            line.startswith('Input Format') or 
            line == 'Measure Format:' or
            line == 'Measure X Y.Z note dynamic duration' or
            line.startswith('Measure') and 'X' in line):  # Skip example measure format
            continue
            
        # Handle section comments (starting with #)
        if line.startswith('# ') and not line.startswith('# Notes:'):
            current_section = {
                'name': line[2:].split('-')[0].strip(),
                'description': line[2:].split('-')[1].strip() if '-' in line else '',
                'start_measure': None,
                'end_measure': None
            }
            song_data['sections'].append(current_section)
            continue
            
        # Handle performance notes
        if line.startswith('# Notes:'):
            in_notes = True
            continue
        if line.startswith('#') and in_notes:
            note = line[2:].strip()
            song_data['performance_notes'].append(note)
            continue
            
        # Handle instrument section headers
        if line.startswith('# '):
            current_instrument = line[2:].strip().lower()
            if current_instrument not in song_data['instruments']:
                song_data['instruments'][current_instrument] = {}
            continue
            
        if line.startswith('Title:'):
            song_data['title'] = line[6:].split('#')[0].strip()
        elif line.startswith('Tempo:'):
            tempo_line = line[6:].strip()
            tempo_parts = tempo_line.split('#')
            song_data['tempo'] = int(tempo_parts[0].strip())
            if len(tempo_parts) > 1:
                song_data['emotional_context']['tempo'] = tempo_parts[1].strip()
        elif line.startswith('Time Signature:'):
            sig_line = line[14:].strip()
            sig_parts = sig_line.split('#')
            song_data['time_signature'] = sig_parts[0].strip()
            if len(sig_parts) > 1:
                song_data['emotional_context']['time_signature'] = sig_parts[1].strip()
        elif line.startswith('Genre:'):
            song_data['genre'] = line[6:].split('#')[0].strip()
        elif line.startswith('Key:'):
            key_line = line[4:].strip()
            key_parts = key_line.split('#')
            song_data['key'] = key_parts[0].strip()
            if len(key_parts) > 1:
                song_data['emotional_context']['key'] = key_parts[1].strip()
        elif line.startswith('Measure'):
            # Parse measure line
            parts = line.split()
            measure_num = int(parts[1])
            
            # Update section measure range
            if current_section:
                if current_section['start_measure'] is None:
                    current_section['start_measure'] = measure_num
                current_section['end_measure'] = measure_num
            
            start_time = float(parts[2])
            note_data = parts[3]
            dynamic = parts[4]
            duration = parts[5]
            
            # Get comment if present
            comment = ' '.join(parts[6:]).strip('# ') if len(parts) > 6 and '#' in line else ''
            
            # Initialize measure if not exists
            if measure_num not in song_data['instruments'].get(current_instrument, {}):
                song_data['instruments'][current_instrument][measure_num] = []
            
            # Convert note data to MIDI pitch
            if note_data.startswith('['):
                # Chord - split and clean each note
                chord_notes = [n.strip() for n in note_data.strip('[]').split(',') if n.strip()]
                if not chord_notes:
                    raise ValueError(f"Empty chord in measure {measure_num}")
                notes = [parse_note(n) for n in chord_notes]
                # Add chord as a single event with multiple notes
                song_data['instruments'][current_instrument][measure_num].append({
                    'notes': notes,  # Use 'notes' instead of 'pitch' for chords
                    'start': start_time,
                    'duration': durations.get(duration, 1.0),
                    'velocity': dynamics.get(dynamic, 80),
                    'comment': comment
                })
            else:
                # Single note
                pitch = parse_note(note_data)
                song_data['instruments'][current_instrument][measure_num].append({
                    'notes': [pitch],  # Use 'notes' for consistency
                    'start': start_time,
                    'duration': durations.get(duration, 1.0),
                    'velocity': dynamics.get(dynamic, 80),
                    'comment': comment
                })
            
            # Add measure to the list if it's not already there
            if measure_num > len(song_data['measures']):
                song_data['measures'].extend([{'chords': [], 'melody': []} for _ in range(measure_num - len(song_data['measures']))])
            
            # Add note to the appropriate part (melody or chords)
            note_event = {
                'notes': notes if note_data.startswith('[') else [pitch],  # Always use 'notes' for consistency
                'beat': start_time,
                'duration': durations.get(duration, 1.0),
                'velocity': dynamics.get(dynamic, 80),
                'comment': comment
            }
            if note_data.startswith('['):
                song_data['measures'][measure_num - 1]['chords'].append(note_event)
            else:
                song_data['measures'][measure_num - 1]['melody'].append(note_event)
    
    return song_data

def generate_midi_direct(song_data: dict, output_dir: str) -> List[str]:
    """Generate MIDI files directly from song data, one for each instrument."""
    output_files = []
    output_dir = Path(output_dir)
    
    # Add time signature and tempo
    time_sig = song_data['time_signature'].strip()  # Remove any extra whitespace
    try:
        numerator, denominator = map(int, time_sig.split('/'))
    except ValueError:
        print(f"Warning: Invalid time signature format '{time_sig}', using 4/4")
        numerator, denominator = 4, 4
    
    # Create instrument instances
    bass = Bass()
    guitar = Guitar()
    drums = Drums()
    
    # Generate patterns for each instrument
    bass_pattern = bass.generate_pattern(song_data, style='walking', genre='classical')
    guitar_pattern = guitar.generate_pattern(song_data, style='arpeggio', genre='classical')
    drums_pattern = drums.generate_pattern(song_data, style='basic', genre='classical')
    
    # Generate a MIDI file for each instrument
    for instrument, pattern in [
        ('bass', bass_pattern),
        ('guitar', guitar_pattern),
        ('drums', drums_pattern)
    ]:
        # Create MIDI file with one track
        midi = MIDIFile(1)
        
        # Add track name
        midi.addTrackName(0, 0, f"{song_data['title']} - {instrument}")
        
        # Add time signature and tempo
        midi.addTimeSignature(0, 0, numerator, int(math.log2(denominator)), 24)
        midi.addTempo(0, 0, song_data['tempo'])
        
        # Add notes from pattern
        for note in pattern:
            midi.addNote(0, 0, note['pitch'], note['start'], note['duration'], note['velocity'])
        
        # Generate output filename for this instrument
        instrument_filename = f"{song_data['title']}_{instrument}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mid"
        instrument_file = output_dir / instrument_filename
        
        # Write the MIDI file
        with open(instrument_file, 'wb') as output_file_obj:
            midi.writeFile(output_file_obj)
        
        output_files.append(str(instrument_file))
    
    return output_files

def test_direct_midi():
    """Test direct MIDI conversion from song file."""
    # Get project root directory
    project_root = Path(__file__).parent.parent
    
    # Input and output paths
    input_file = project_root / 'input' / 'songs' / 'Piano_test.txt'
    output_dir = project_root / 'output'
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Load song data
        print(f"Loading song from {input_file}...")
        song_data = load_song_direct(str(input_file))
        print(f"Loaded song: {song_data['title']}")
        print(f"Tempo: {song_data['tempo']}")
        print(f"Time Signature: {song_data['time_signature']}")
        print(f"Key: {song_data['key']}")
        print(f"Instruments: {', '.join(song_data['instruments'].keys())}")
        
        # Generate MIDI files
        print(f"\nGenerating MIDI files...")
        output_files = generate_midi_direct(song_data, str(output_dir))
        print(f"Successfully generated {len(output_files)} MIDI files:")
        for file in output_files:
            print(f"  - {file}")
        
    except Exception as e:
        print(f"Error: {e}")
        raise

def test_generate_midi():
    # Read the piano test file
    project_root = Path(__file__).parent.parent
    input_file = project_root / 'input' / 'songs' / 'Piano_test.txt'
    
    with open(input_file, 'r') as f:
        piano_content = f.read()
    
    # Create instances of each instrument
    piano = Piano()
    bass = Bass()
    guitar = Guitar()
    drums = Drums()
    
    # Parse the tempo and key from the piano file
    tempo = 60  # From the test file
    key = "Em"  # E minor
    
    # Generate MIDI for each instrument
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = project_root / 'output'
    output_dir.mkdir(exist_ok=True)
    
    # Parse the piano content into song data
    song_data = load_song_direct(input_file)
    
    # Piano - Use the test file directly
    piano_pattern = piano.generate_pattern(song_data, style='classical', genre='classical')
    piano_midi = MIDIFile(1)
    piano_midi.addTempo(0, 0, tempo)
    piano_midi.addTimeSignature(0, 0, 4, 2, 24)  # 4/4 time
    for note in piano_pattern:
        piano_midi.addNote(0, 0, note['pitch'], note['start'], note['duration'], note['velocity'])
    with open(output_dir / f'piano_{timestamp}.mid', 'wb') as f:
        piano_midi.writeFile(f)
    
    # Bass - Create a supportive bass line in E minor
    bass_pattern = """
    MIDI Bass Line
    =============
    Title: Bass Support for Lament
    Tempo: 60
    Time Signature: 4/4
    Key: E minor
    
    Measure 1 1.0 E2 mf half
    Measure 1 3.0 B2 mp quarter
    Measure 1 4.0 G2 mp quarter
    
    Measure 2 1.0 E2 mf half
    Measure 2 3.0 B2 mp quarter
    Measure 2 4.0 G2 mp quarter
    
    Measure 3 1.0 E2 mf half
    Measure 3 3.0 D2 mp quarter
    Measure 3 4.0 B2 mp quarter
    
    Measure 4 1.0 A2 mf half
    Measure 4 3.0 Fs2 mp quarter
    Measure 4 4.0 D2 mp quarter
    
    Measure 5 1.0 E2 mf half
    Measure 5 3.0 B2 mp quarter
    Measure 5 4.0 G2 mp quarter
    
    Measure 6 1.0 D2 mf half
    Measure 6 3.0 A2 mp quarter
    Measure 6 4.0 Fs2 mp quarter
    
    Measure 7 1.0 E2 mf half
    Measure 7 3.0 B2 mp quarter
    Measure 7 4.0 G2 mp quarter
    
    Measure 8 1.0 E2 pp whole
    """
    bass_pattern = bass.generate_pattern(song_data, style='walking', genre='classical')
    bass_midi = MIDIFile(1)
    bass_midi.addTempo(0, 0, tempo)
    bass_midi.addTimeSignature(0, 0, 4, 2, 24)  # 4/4 time
    for note in bass_pattern:
        bass_midi.addNote(0, 0, note['pitch'], note['start'], note['duration'], note['velocity'])
    with open(output_dir / f'bass_{timestamp}.mid', 'wb') as f:
        bass_midi.writeFile(f)
    
    # Guitar - Gentle arpeggiated chords
    guitar_pattern = guitar.generate_pattern(song_data, style='arpeggio', genre='classical')
    guitar_midi = MIDIFile(1)
    guitar_midi.addTempo(0, 0, tempo)
    guitar_midi.addTimeSignature(0, 0, 4, 2, 24)  # 4/4 time
    for note in guitar_pattern:
        guitar_midi.addNote(0, 0, note['pitch'], note['start'], note['duration'], note['velocity'])
    with open(output_dir / f'guitar_{timestamp}.mid', 'wb') as f:
        guitar_midi.writeFile(f)
    
    # Drums - Very minimal, just light brushes for atmosphere
    drums_pattern = drums.generate_pattern(song_data, style='basic', genre='classical')
    drums_midi = MIDIFile(1)
    drums_midi.addTempo(0, 0, tempo)
    drums_midi.addTimeSignature(0, 0, 4, 2, 24)  # 4/4 time
    for note in drums_pattern:
        drums_midi.addNote(0, 0, note['pitch'], note['start'], note['duration'], note['velocity'])
    with open(output_dir / f'drums_{timestamp}.mid', 'wb') as f:
        drums_midi.writeFile(f)

if __name__ == "__main__":
    try:
        test_generate_midi()
        print("Successfully generated MIDI files!")
    except Exception as e:
        print(f"Error generating MIDI files: {e}")
        raise 