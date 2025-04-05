# txt sting to mid File, no conversion! 

import os

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

    choice = int(input("Select a song file by number: "))
    if choice < 1 or choice > len(files):
        raise ValueError("Invalid selection.")

    return os.path.join(directory, files[choice - 1])

def get_versioned_filename(base_filename):
    """Get a versioned filename if the base filename already exists."""
    if not os.path.exists(base_filename):
        return base_filename
    
    # Split the filename into name and extension
    name, ext = os.path.splitext(base_filename)
    
    # Try with version numbers until we find one that doesn't exist
    version = 1
    while True:
        versioned_filename = f"{name}_v{version}{ext}"
        if not os.path.exists(versioned_filename):
            return versioned_filename
        version += 1

def save_hex_to_midi(input_file, output_file):
    """Save the hex string from input file directly as a MIDI file."""
    try:
        # Read the hex string from the input file
        with open(input_file, 'r') as f:
            hex_string = f.read()
        
        # Convert hex to bytes
        binary_data = bytes.fromhex(hex_string)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Get versioned filename if file already exists
        versioned_midi_file = get_versioned_filename(output_file)
        
        # Write binary data to MIDI file
        with open(versioned_midi_file, 'wb') as f:
            f.write(binary_data)
        
        print(f"MIDI file saved as: {versioned_midi_file}")
        print(f"Total file size: {len(binary_data)} bytes")
        
    except Exception as e:
        print(f"Error saving MIDI file: {str(e)}")
        raise

def main():
    input_directory = os.path.join('Grok', 'GrokMidi', 'Input')
    output_directory = os.path.join('Grok', 'GrokMidi', 'Output')
    
    try:
        input_file = select_song_file(input_directory)
        output_file = os.path.join(output_directory, os.path.basename(input_file).replace('.txt', '.mid'))
        
        save_hex_to_midi(input_file, output_file)
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()

