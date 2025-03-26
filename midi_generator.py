from midiutil import MIDIFile
import os
import re
from pathlib import Path
from datetime import datetime

class MIDIGenerator:
    def __init__(self):
        # MIDI note mapping (C4 = 60)
        self.note_to_midi = {
            'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11
        }
        
        # Duration mapping (quarter note = 1.0 beats)
        self.duration_to_beats = {
            'whole': 4.0,
            'half': 2.0,
            'quarter': 1.0,
            'eighth': 0.5,
            'sixteenth': 0.25,
            'thirtysecond': 0.125
        }
        
        # Dynamics mapping
        self.dynamics_to_velocity = {
            'pp': 20,    # pianissimo
            'p': 40,     # piano
            'mp': 60,    # mezzo-piano
            'mf': 80,    # mezzo-forte
            'f': 100,    # forte
            'ff': 120    # fortissimo
        }

    def note_to_midi_number(self, note_str):
        """Convert note string (e.g., 'A4') to MIDI number"""
        match = re.match(r'([A-G])(\d+)', note_str)
        if match:
            note, octave = match.groups()
            midi_number = self.note_to_midi[note] + (int(octave) + 1) * 12
            return midi_number
        return None

    def parse_duration(self, duration_str):
        """Convert duration string to beats"""
        return self.duration_to_beats.get(duration_str, 1.0)

    def parse_dynamics(self, dynamics_str):
        """Convert dynamics string to velocity"""
        return self.dynamics_to_velocity.get(dynamics_str, 80)

    def create_midi_file(self, song_data, output_path, tempo=120):
        """Create a MIDI file from song data"""
        try:
            print(f"\nCreating MIDI file: {output_path}")
            print(f"Tempo: {tempo}")
            print(f"Number of measures: {len(song_data['measures'])}")
            
            # Create a MIDI file with one track
            midi = MIDIFile(1, adjust_origin=True)
            
            # Set the tempo
            midi.addTempo(0, 0, tempo)
            
            # Add notes to the track
            current_time = 0
            total_notes = 0
            
            for measure_num, measure in enumerate(song_data['measures'], 1):
                print(f"\nProcessing measure {measure_num}")
                
                # Create a list of all notes in the measure with their start times
                measure_notes = []
                
                # Process each note or chord in the measure
                for note_data in measure:
                    if isinstance(note_data, list):  # Chord
                        for pitch_data in note_data:
                            measure_notes.append({
                                'pitch': pitch_data['pitch'],
                                'duration': pitch_data['duration'],
                                'velocity': pitch_data['velocity'],
                                'start': pitch_data['start'],
                                'is_chord': True
                            })
                    else:  # Single note
                        measure_notes.append({
                            'pitch': note_data['pitch'],
                            'duration': note_data['duration'],
                            'velocity': note_data['velocity'],
                            'start': note_data['start'],
                            'is_chord': False
                        })
                
                # Sort notes by start time
                measure_notes.sort(key=lambda x: (x['start'], x['is_chord']))
                print(f"Measure {measure_num} has {len(measure_notes)} notes")
                
                # Group notes that start at the same time
                current_start = -1
                current_chord = []
                
                for note in measure_notes:
                    if note['start'] != current_start:
                        # Add previous chord if exists
                        if current_chord:
                            # Calculate the actual start time within the measure
                            note_start = current_time + current_start
                            
                            # Add each note in the chord
                            for chord_note in current_chord:
                                # Ensure all values are within valid MIDI ranges
                                pitch_value = max(0, min(127, chord_note['pitch']))
                                velocity = max(0, min(127, chord_note['velocity']))
                                duration = max(0.1, chord_note['duration'])
                                
                                midi.addNote(0, 0, pitch_value, note_start, duration, velocity)
                                total_notes += 1
                                print(f"Added chord note: pitch {pitch_value}, start {note_start}, duration {duration}, velocity {velocity}")
                            
                            current_chord = []
                        
                        current_start = note['start']
                    
                    if note['is_chord']:
                        current_chord.append(note)
                    else:
                        # Add single note immediately
                        note_start = current_time + note['start']
                        
                        # Ensure all values are within valid MIDI ranges
                        pitch_value = max(0, min(127, note['pitch']))
                        velocity = max(0, min(127, note['velocity']))
                        duration = max(0.1, note['duration'])
                        
                        midi.addNote(0, 0, pitch_value, note_start, duration, velocity)
                        total_notes += 1
                        print(f"Added single note: pitch {pitch_value}, start {note_start}, duration {duration}, velocity {velocity}")
                
                # Add any remaining chord
                if current_chord:
                    note_start = current_time + current_start
                    for chord_note in current_chord:
                        pitch_value = max(0, min(127, chord_note['pitch']))
                        velocity = max(0, min(127, chord_note['velocity']))
                        duration = max(0.1, chord_note['duration'])
                        
                        midi.addNote(0, 0, pitch_value, note_start, duration, velocity)
                        total_notes += 1
                        print(f"Added final chord note: pitch {pitch_value}, start {note_start}, duration {duration}, velocity {velocity}")
                
                # Move to next measure
                current_time += 4.0  # Assuming 4/4 time signature
            
            # Write the MIDI file
            with open(output_path, "wb") as output_file:
                midi.writeFile(output_file)
            
            print(f"\nMIDI file created successfully:")
            print(f"Total measures: {len(song_data['measures'])}")
            print(f"Total notes: {total_notes}")
            print(f"Output file: {output_path}")
            return True
        except Exception as e:
            print(f"Error creating MIDI file: {e}")
            import traceback
            print("Traceback:")
            traceback.print_exc()
            return False

def validate_song_format(lines):
    """Validate the song file format and return error messages if any"""
    errors = []
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
            
        # Skip any non-note lines
        if any(word in line.lower() for word in ['title:', 'key:', 'time:', 'tempo:', 'mood:', 'right', 'left', 'rh:', 'lh:', 'measure']):
            continue
            
        # Check note format
        parts = line.split()
        if not parts:
            continue
            
        # Check note format
        note = parts[0]
        if note.startswith('['):  # Chord
            if not note.endswith(']'):
                errors.append(f"Line {i}: Chord must be enclosed in square brackets")
            notes = note[1:-1].split(',')
            for n in notes:
                if not re.match(r'^[A-G]#?[0-9]$', n.strip()):
                    errors.append(f"Line {i}: Invalid note in chord: {n}")
        else:  # Single note
            if not re.match(r'^[A-G]#?[0-9]$', note):
                errors.append(f"Line {i}: Invalid note format: {note}")
    
    return errors

def convert_to_standard_format(lines):
    """Convert any input format to match our standard format"""
    standardized_lines = []
    current_measure = 1
    measure_notes = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Skip header lines and hand labels
        if any(word in line.lower() for word in ['title:', 'key:', 'time:', 'tempo:', 'mood:', 'right', 'left', 'rh:', 'lh:']):
            continue
            
        # Handle measure markers
        if any(word in line.lower() for word in ['measure', 'bar', '|']):
            if measure_notes:
                standardized_lines.append(f"[Measure {current_measure}]")
                standardized_lines.extend(measure_notes)
                measure_notes = []
                current_measure += 1
            continue
            
        # Process note line
        parts = line.split()
        if not parts:
            continue
            
        # Extract note and duration
        note = parts[0]
        duration = 'quarter'  # default duration
        
        # Look for duration in the line
        for word in parts:
            if word.lower() in ['whole', 'half', 'quarter', 'eighth', 'sixteenth']:
                duration = word.lower()
        
        # Format the note line
        note_line = f"{note} {duration} mf"  # Using default mf dynamics
        measure_notes.append(note_line)
    
    # Add the last measure
    if measure_notes:
        standardized_lines.append(f"[Measure {current_measure}]")
        standardized_lines.extend(measure_notes)
    
    return standardized_lines

def parse_song_file(file_path):
    """Parse a song file and return song data"""
    try:
        print(f"\nParsing file: {file_path}")
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Create MIDIGenerator instance
        generator = MIDIGenerator()
        
        song_data = {
            'title': '',
            'key': '',
            'time_signature': '',
            'tempo': 120,
            'measures': {}
        }
        
        print("\nProcessing lines:")
        # Process the lines
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            print(f"\nLine {i}: '{line}'")
            
            # Parse header information
            if line.startswith('Title:'):
                song_data['title'] = line[6:].strip()
                print(f"Found title: {song_data['title']}")
            elif line.startswith('Key:'):
                song_data['key'] = line[4:].strip()
                print(f"Found key: {song_data['key']}")
            elif line.startswith('Time Signature:'):
                song_data['time_signature'] = line[14:].strip()
                print(f"Found time signature: {song_data['time_signature']}")
            elif line.startswith('Tempo:'):
                song_data['tempo'] = int(line[6:].strip().split()[0])
                print(f"Found tempo: {song_data['tempo']}")
            
            # Parse note line
            elif line.startswith('Measure'):
                try:
                    # Split the line into parts
                    parts = line.split()
                    if len(parts) < 6:
                        print(f"Warning: Invalid note line format: {line}")
                        print("Expected format: Measure X Y.Z Note Dynamic Duration")
                        continue
                    
                    # Extract all variables
                    measure_num = int(parts[1])
                    start_time = float(parts[2])  # Y.Z format
                    note_str = parts[3]
                    dynamics = parts[4]
                    duration = parts[5]
                    
                    print(f"Processing note: Measure {measure_num}, Start {start_time}, Note {note_str}, Dynamics {dynamics}, Duration {duration}")
                    
                    # Validate measure number (1-1000)
                    if not (1 <= measure_num <= 1000):
                        print(f"Warning: Invalid measure number {measure_num}. Must be between 1 and 1000.")
                        continue
                    
                    # Validate start time format (Y.Z)
                    if not (0.0 <= start_time <= 4.0):  # Assuming 4/4 time
                        print(f"Warning: Invalid start time {start_time}. Must be between 0.0 and 4.0.")
                        continue
                    
                    # Initialize measure if it doesn't exist
                    if measure_num not in song_data['measures']:
                        song_data['measures'][measure_num] = []
                    
                    # Handle both single notes and chords
                    if note_str.startswith('[') and note_str.endswith(']'):
                        # Process chord
                        chord_notes = note_str[1:-1].split(',')
                        chord_data = []
                        for chord_note in chord_notes:
                            chord_note = chord_note.strip()
                            midi_number = generator.note_to_midi_number(chord_note)
                            if midi_number is not None:
                                chord_data.append({
                                    'pitch': midi_number,
                                    'duration': generator.parse_duration(duration),
                                    'velocity': generator.parse_dynamics(dynamics),
                                    'start': start_time,
                                    'is_chord': True
                                })
                                print(f"Added chord note: {chord_note} -> MIDI {midi_number}")
                            else:
                                print(f"Warning: Invalid note in chord: {chord_note}")
                        if chord_data:
                            song_data['measures'][measure_num].extend(chord_data)
                    else:
                        # Process single note
                        midi_number = generator.note_to_midi_number(note_str)
                        if midi_number is not None:
                            note_data = {
                                'pitch': midi_number,
                                'duration': generator.parse_duration(duration),
                                'velocity': generator.parse_dynamics(dynamics),
                                'start': start_time,
                                'is_chord': False
                            }
                            song_data['measures'][measure_num].append(note_data)
                            print(f"Added note: {note_str} -> MIDI {midi_number}")
                        else:
                            print(f"Warning: Invalid note format: {note_str}")
                
                except (ValueError, IndexError) as e:
                    print(f"Warning: Error parsing note line: {line}")
                    print(f"Error details: {e}")
                    continue
        
        # Convert measures dictionary to list
        if not song_data['measures']:
            print("Warning: No valid measures found in the song file")
            return None
            
        max_measure = max(song_data['measures'].keys())
        song_data['measures'] = [song_data['measures'].get(i, []) for i in range(1, max_measure + 1)]
        
        print(f"\nParsing complete. Found {len(song_data['measures'])} measures")
        return song_data
    except Exception as e:
        print(f"Error parsing song file: {e}")
        import traceback
        print("Traceback:")
        traceback.print_exc()
        return None

def get_next_version(output_dir, base_name):
    """Get the next version number for a file"""
    existing_files = [f for f in os.listdir(output_dir) if f.startswith(base_name) and f.endswith('.mid')]
    if not existing_files:
        return 1
    
    # Extract version numbers from existing files
    versions = []
    for file in existing_files:
        try:
            # Extract version number from filename (e.g., "song_v1.mid" -> 1)
            version = int(file.split('_v')[1].split('.')[0])
            versions.append(version)
        except (IndexError, ValueError):
            continue
    
    return max(versions) + 1 if versions else 1

def process_song(input_file, output_dir):
    """Process a single song file"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Read headers for filename
    title = "Untitled"
    key = "C"
    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('Title:'):
                title = line[6:].strip()
            elif line.startswith('Key:'):
                key = line[4:].strip()
    
    # Create filename from title and key
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_key = "".join(c for c in key if c.isalnum() or c in (' ', '-', '_')).strip()
    base_name = f"{safe_title}_{safe_key}"
    
    # Get next version number
    version = get_next_version(output_dir, base_name)
    output_file = os.path.join(output_dir, f"{base_name}_v{version}.mid")
    
    # Parse the song file
    song_data = parse_song_file(input_file)
    if not song_data:
        print(f"Failed to parse {input_file}")
        return False
    
    # Create MIDI file
    generator = MIDIGenerator()
    return generator.create_midi_file(song_data, output_file, song_data['tempo'])

def process_all_songs(input_dir, output_dir):
    """Process all song files in the input directory"""
    success_count = 0
    total_count = 0
    
    for file in os.listdir(input_dir):
        if file.endswith('.txt'):
            total_count += 1
            input_file = os.path.join(input_dir, file)
            if process_song(input_file, output_dir):
                success_count += 1
    
    print(f"\nProcessed {success_count} out of {total_count} songs successfully")

def copy_template(template_name, new_name):
    """Copy a template file to create a new song file"""
    template_dir = os.path.join(os.path.dirname(__file__), 'input', 'templates')
    songs_dir = os.path.join(os.path.dirname(__file__), 'input', 'songs')
    
    # Ensure directories exist
    os.makedirs(template_dir, exist_ok=True)
    os.makedirs(songs_dir, exist_ok=True)
    
    template_file = os.path.join(template_dir, f"{template_name}.txt")
    new_file = os.path.join(songs_dir, f"{new_name}.txt")
    
    if not os.path.exists(template_file):
        print(f"Template '{template_name}' not found")
        return False
    
    try:
        with open(template_file, 'r') as src, open(new_file, 'w') as dst:
            dst.write(src.read())
        print(f"Created new song file: {new_name}.txt")
        return True
    except Exception as e:
        print(f"Error copying template: {e}")
        return False

def main():
    # Define directories
    input_dir = os.path.join(os.path.dirname(__file__), 'input', 'songs')
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    
    # Create directories if they don't exist
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Get list of song files
    song_files = [f for f in os.listdir(input_dir) if f.endswith('.txt')]
    
    if not song_files:
        print("No song files found in input/songs directory")
        print("Please add your song files to the input/songs directory")
        return
    
    print("\nAvailable songs:")
    for i, file in enumerate(song_files, 1):
        print(f"{i}. {file}")
    
    print("\nOptions:")
    print("1. Convert a specific song")
    print("2. Convert all songs")
    
    # Get menu choice
    while True:
        try:
            choice = input("\nEnter your choice (1 or 2): ").strip()
            if choice in ['1', '2']:
                break
            print("Please enter 1 or 2")
        except ValueError:
            print("Please enter 1 or 2")
    
    if choice == '1':
        # Get song choice
        while True:
            try:
                print("\nEnter the number of the song to convert (1-{})".format(len(song_files)))
                song_choice = input("> ").strip()
                song_choice = int(song_choice) - 1
                if 0 <= song_choice < len(song_files):
                    break
                print(f"Please enter a number between 1 and {len(song_files)}")
            except ValueError:
                print("Please enter a valid number")
        
        input_file = os.path.join(input_dir, song_files[song_choice])
        print(f"\nConverting: {song_files[song_choice]}")
        process_song(input_file, output_dir)
    
    else:  # choice == '2'
        print("\nConverting all songs...")
        process_all_songs(input_dir, output_dir)

if __name__ == "__main__":
    main() 