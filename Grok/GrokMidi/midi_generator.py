import os
import re

def clean_hex_string(hex_string):
    """Clean the hex string by removing comments and whitespace."""
    hex_string = re.sub(r'//.*$', '', hex_string, flags=re.MULTILINE)
    return ''.join(hex_string.split())

def read_midi_binary(input_file):
    """Read and parse the MIDI binary text file."""
    with open(input_file, 'r') as f:
        content = f.read()
    return clean_hex_string(content)

def list_input_files(directory):
    """List all text files in the input directory."""
    return [f for f in os.listdir(directory) if f.endswith('.txt')]

def select_song_file(directory):
    """Prompt the user to select a song file from the input directory."""
    files = list_input_files(directory)
    if not files:
        raise FileNotFoundError("No song files found in the input directory.")

    print("Available song files:")
    for i, file in enumerate(files, start=1):
        print(f"{i}. {file}")

    while True:
        try:
            choice = int(input("Select a song file by number: "))
            if 1 <= choice <= len(files):
                return os.path.join(directory, files[choice - 1])
            else:
                print(f"Please enter a number between 1 and {len(files)}.")
        except ValueError:
            print("Please enter a valid number.")

def save_hex_to_text(hex_data, output_path):
    """Save hex data to a text file for debugging."""
    text_path = output_path.replace('.mid', '_hex.txt')
    formatted_hex = ' '.join(hex_data[i:i+2] for i in range(0, len(hex_data), 2))
    formatted_hex = '\n'.join(formatted_hex[i:i+32] for i in range(0, len(formatted_hex), 32))
    with open(text_path, 'w') as f:
        f.write("Full MIDI Hex:\n")
        f.write(formatted_hex)
    print(f"Hex data saved as: {text_path}")

def create_midi_file(hex_data, output_path):
    """Create a MIDI file by writing raw bytes, handling full files or track chunks."""
    try:
        print(f"Input hex data: {hex_data}")
        
        # Strip leading/trailing '00' pairs
        while hex_data.startswith('00'):
            hex_data = hex_data[2:]
        while hex_data.endswith('00'):
            hex_data = hex_data[:-2]
        
        # Check if it’s a full MIDI file (starts with MThd)
        if hex_data.startswith('4D546864'):
            full_data = hex_data
        else:
            # Assume track chunk or raw events; construct a full file
            if hex_data.startswith('4D54726B'):
                track_content = hex_data[16:]  # Skip MTrk + length
            else:
                track_content = hex_data  # Raw events
            track_length = len(track_content) // 2
            track_length_hex = format(track_length, '08x')
            full_track = '4D54726B' + track_length_hex + track_content
            header = '4D54686400000006000000010060'  # Format 0, 96 PPQ
            full_data = header + full_track
        
        # Convert to bytes
        binary_data = bytes.fromhex(full_data)
        
        # Save hex version for debugging
        save_hex_to_text(full_data, output_path)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write binary data to MIDI file
        with open(output_path, 'wb') as f:
            f.write(binary_data)
        
        print(f"MIDI file saved as: {output_path}")
        print(f"Total file size: {len(binary_data)} bytes")
        
    except Exception as e:
        print(f"Error creating MIDI file: {str(e)}")
        raise

def main():
    input_directory = os.path.join('Grok', 'GrokMidi', 'Input')
    output_directory = os.path.join('Grok', 'GrokMidi', 'Output')

    try:
        input_file = select_song_file(input_directory)
        output_file = os.path.join(output_directory, os.path.basename(input_file).replace('.txt', '.mid'))

        hex_data = read_midi_binary(input_file)
        create_midi_file(hex_data, output_file)
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()