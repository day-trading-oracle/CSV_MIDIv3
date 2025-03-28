from midiutil import MIDIFile
import os
import json
from src.midi_generator import generate_midi
from src.accompaniment_generator import GenreManager

def note_to_midi(note_name):
    """Convert note name (e.g., 'C5') to MIDI note number"""
    notes = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
    note = note_name[0].upper()
    if note not in notes:
        raise ValueError(f"Invalid note name: {note}")
    try:
        octave = int(note_name[1:])
    except (ValueError, IndexError):
        raise ValueError(f"Invalid octave in note name: {note_name}")
    return 12 * (octave + 1) + notes[note]

def dynamic_to_velocity(dynamic):
    """Convert dynamic marking to MIDI velocity"""
    dynamics = {
        'pp': 20, 'p': 40, 'mp': 60, 'mf': 80, 'f': 100, 'ff': 120
    }
    return dynamics.get(dynamic.lower(), 80)  # Default to mf if not found

def duration_to_quarters(duration):
    """Convert duration text to quarter notes"""
    durations = {
        'whole': 4.0,
        'half': 2.0,
        'quarter': 1.0,
        'eighth': 0.5,
        'sixteenth': 0.25
    }
    return durations.get(duration.lower(), 1.0)  # Default to quarter note if not found

def list_input_files():
    """List all available input files in the input directory"""
    input_dir = os.path.join(os.path.dirname(__file__), 'input', 'songs')
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        print("Created input/songs directory. Please add your song text files there.")
        return []
    
    files = [f for f in os.listdir(input_dir) if f.endswith('.txt')]
    if not files:
        print("No input files found in the input/songs directory.")
        print("Please add text files containing song data to the input/songs directory.")
        print("Format: Each line should be in the format: Measure X Y.Z note dynamic duration")
        print("Example: Measure 1 1.0 C5 f quarter")
        return []
    
    print("\nAvailable input files:")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")
    return files

def load_song_data(filename):
    """Load song data from a text file"""
    input_dir = os.path.join(os.path.dirname(__file__), 'input', 'songs')
    filepath = os.path.join(input_dir, filename)
    
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File {filename} not found in {input_dir}")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

    song_data = {
        'title': 'Untitled',
        'key': 'C',
        'time_signature': '4/4',
        'tempo': 120,
        'measures': []
    }

    current_measure = []
    current_measure_number = 1
    line_number = 0

    for line in lines:
        line_number += 1
        line = line.strip()
        if not line:
            continue

        # Parse header information
        if line.startswith('Title:'):
            song_data['title'] = line[6:].strip()
            continue
        elif line.startswith('Key:'):
            song_data['key'] = line[4:].strip()
            continue
        elif line.startswith('Time Signature:'):
            try:
                time_sig = line[14:].strip()
                if '/' in time_sig:
                    num, den = time_sig.split('/')
                    if num.isdigit() and den.isdigit():
                        song_data['time_signature'] = time_sig
                    else:
                        print(f"Warning: Invalid time signature format: {time_sig}. Using default 4/4.")
                else:
                    print(f"Warning: Invalid time signature format: {time_sig}. Using default 4/4.")
            except Exception as e:
                print(f"Warning: Invalid time signature format: {e}. Using default 4/4.")
            continue
        elif line.startswith('Tempo:'):
            try:
                song_data['tempo'] = int(line[6:].strip())
            except ValueError:
                print(f"Warning: Invalid tempo value. Using default 120.")
            continue

        # Parse measure data
        parts = line.split()
        if len(parts) < 5:
            print(f"Warning: Invalid line format at line {line_number}: {line}")
            continue

        if parts[0] == 'Measure':
            try:
                measure_num = int(parts[1])
                if measure_num != current_measure_number:
                    if current_measure:
                        song_data['measures'].append(current_measure)
                    current_measure = []
                    current_measure_number = measure_num

                start_time = float(parts[2])
                note_data = parts[3]
                dynamic = parts[4]
                duration = parts[5] if len(parts) > 5 else 'quarter'

                # Convert note data to MIDI format
                if note_data.startswith('[') and note_data.endswith(']'):
                    # Handle chord
                    chord_notes = [note.strip() for note in note_data[1:-1].split(',')]
                    chord_data = []
                    for note in chord_notes:
                        try:
                            if not note:  # Skip empty notes
                                continue
                            chord_data.append({
                                'pitch': note_to_midi(note),
                                'duration': duration_to_quarters(duration),
                                'start': start_time - 1,  # Convert to 0-based time
                                'velocity': dynamic_to_velocity(dynamic)
                            })
                        except ValueError as e:
                            print(f"Warning: Invalid note in chord at line {line_number}: {e}")
                            continue
                    if chord_data:  # Only add if we have valid notes
                        current_measure.append(chord_data)
                else:
                    # Handle single note
                    try:
                        note_data = {
                            'pitch': note_to_midi(note_data),
                            'duration': duration_to_quarters(duration),
                            'start': start_time - 1,  # Convert to 0-based time
                            'velocity': dynamic_to_velocity(dynamic)
                        }
                        current_measure.append(note_data)
                    except ValueError as e:
                        print(f"Warning: Invalid note at line {line_number}: {e}")
                        continue
            except (ValueError, IndexError) as e:
                print(f"Warning: Invalid measure data at line {line_number}: {e}")
                continue

    # Add the last measure
    if current_measure:
        song_data['measures'].append(current_measure)

    return song_data

def create_test_song():
    """Create a test song with a C major scale"""
    # C major scale (C4 to C5)
    c_major_scale = [60, 62, 64, 65, 67, 69, 71, 72]  # MIDI note numbers
    
    # Create song data structure
    song_data = {
        'title': 'Test Scale',
        'tempo': 120,
        'time_signature': '4/4',
        'instrument': 0,  # Piano
        'measures': []
    }
    
    # Create two measures of the scale
    for measure in range(2):
        measure_notes = []
        for i, pitch in enumerate(c_major_scale):
            note_data = {
                'pitch': pitch,
                'duration': 0.5,  # Eighth notes
                'start': i * 0.5,  # Start time within measure
                'velocity': 80
            }
            measure_notes.append(note_data)
        song_data['measures'].append(measure_notes)
    
    return song_data

def select_genre():
    """Let user select a genre"""
    genre_manager = GenreManager()
    genres = list(genre_manager.genres.keys())
    
    print("\nAvailable genres:")
    for i, genre in enumerate(genres, 1):
        print(f"{i}. {genre}")
    
    while True:
        try:
            choice = int(input("\nSelect genre number: "))
            if 1 <= choice <= len(genres):
                return genres[choice - 1]
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def select_accompaniment_style():
    """Let user select accompaniment style"""
    styles = ['basic', 'none']
    print("\nAvailable accompaniment styles:")
    for i, style in enumerate(styles, 1):
        print(f"{i}. {style}")
    
    while True:
        try:
            choice = int(input("\nSelect accompaniment style number: "))
            if 1 <= choice <= len(styles):
                return styles[choice - 1]
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def select_bass_options():
    """Let user configure bass options"""
    print("\nBass Options:")
    enable_bass = input("Enable bass track? (y/n): ").lower() == 'y'
    if enable_bass:
        styles = ['walking', 'simple']
        print("\nAvailable bass styles:")
        for i, style in enumerate(styles, 1):
            print(f"{i}. {style}")
        
        while True:
            try:
                choice = int(input("\nSelect bass style number: "))
                if 1 <= choice <= len(styles):
                    return {
                        'enable_bass': True,
                        'bass_style': styles[choice - 1]
                    }
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
    return {'enable_bass': False}

def main():
    print("MIDI File Generator")
    print("------------------")
    
    # List available input files
    input_files = list_input_files()
    
    if not input_files:
        print("\nUsing default test song (C major scale)...")
        song_data = create_test_song()
    else:
        while True:
            try:
                choice = int(input("\nSelect input file number (or 0 for default test song): "))
                if choice == 0:
                    song_data = create_test_song()
                    break
                elif 1 <= choice <= len(input_files):
                    selected_file = input_files[choice - 1]
                    song_data = load_song_data(selected_file)
                    if song_data:
                        break
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
    
    if not song_data:
        print("Failed to load song data. Using default test song.")
        song_data = create_test_song()
    
    # Get user preferences
    genre = select_genre()
    accompaniment_style = select_accompaniment_style()
    bass_options = select_bass_options()
    
    # Update song data with bass options
    song_data.update(bass_options)
    
    print(f"\nGenerating MIDI with {accompaniment_style} accompaniment in {genre} style...")
    if bass_options['enable_bass']:
        print(f"Bass track enabled with {bass_options['bass_style']} style")
    
    output_file = generate_midi(
        song_data,
        accompaniment_style=accompaniment_style,
        genre=genre
    )
    
    if output_file:
        print(f"Successfully generated: {output_file}")
    else:
        print("Failed to generate MIDI file")

if __name__ == "__main__":
    main() 