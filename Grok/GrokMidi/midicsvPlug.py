import os
import sys
import py_midicsv.midicsv as midicsv
import py_midicsv.csvmidi as csvmidi
from py_midicsv.midi.fileio import FileWriter

def list_files(directory):
    """List all files in the specified directory."""
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        return []
    
    files = []
    for file in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, file)):
            files.append(file)
    return sorted(files)

def select_file(directory, file_type=None):
    """Let the user select a file from the directory."""
    files = list_files(directory)
    
    if not files:
        print(f"No files found in {directory}")
        return None
    
    print(f"\nAvailable files in {directory}:")
    filtered_files = []
    for i, file in enumerate(files, 1):
        if file_type is None or file.lower().endswith(file_type.lower()):
            print(f"{i}. {file}")
            filtered_files.append(file)
    
    if not filtered_files:
        print(f"No {file_type} files found in {directory}")
        return None
    
    while True:
        try:
            choice = int(input("\nSelect a file number: "))
            if 1 <= choice <= len(filtered_files):
                selected_file = filtered_files[choice - 1]
                return os.path.join(directory, selected_file)
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a number.")

def get_output_filename(input_file, output_dir, target_ext):
    """Generate an output filename in the Output directory."""
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(output_dir, base_name + target_ext)
    
    # Check if file already exists and add version number if needed
    counter = 1
    while os.path.exists(output_file):
        output_file = os.path.join(output_dir, f"{base_name}_v{counter}{target_ext}")
        counter += 1
    
    return output_file

def main():
    print("MIDI-CSV Converter")
    print("=================")
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, "Input")
    output_dir = os.path.join(script_dir, "Output")
    
    # Ask user to select file type
    print("\nSelect file type:")
    print("1. MIDI file (.mid, .midi)")
    print("2. CSV file (.csv)")
    print("3. All files")
    
    while True:
        try:
            type_choice = int(input("Enter your choice (1, 2, or 3): "))
            if type_choice == 1:
                file_type = ".mid"
                break
            elif type_choice == 2:
                file_type = ".csv"
                break
            elif type_choice == 3:
                file_type = None
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        except ValueError:
            print("Please enter a number.")
    
    # Select input file from Input directory
    input_file = select_file(input_dir, file_type)
    if not input_file:
        print("No file selected. Exiting.")
        return
    
    # Determine conversion type based on file extension
    input_ext = os.path.splitext(input_file)[1].lower()
    
    # Automatically generate output filename in the Output directory
    if input_ext == '.mid' or input_ext == '.midi':
        output_file = get_output_filename(input_file, output_dir, ".csv")
    elif input_ext == '.csv':
        output_file = get_output_filename(input_file, output_dir, ".mid")
    else:
        print("Unsupported file format. Please use .mid, .midi, or .csv files.")
        return
    
    print(f"Output will be saved to: {output_file}")
    
    try:
        if input_ext == '.mid' or input_ext == '.midi':
            # Convert MIDI to CSV
            print(f"Converting {input_file} to CSV...")
            with open(input_file, 'rb') as midi_file:
                csv_data = midicsv.parse(midi_file)
            with open(output_file, 'w') as csv_file:
                csv_file.writelines(csv_data)
            print(f"Successfully converted to {output_file}")
            
        elif input_ext == '.csv':
            # Convert CSV to MIDI
            print(f"Converting {input_file} to MIDI...")
            with open(input_file, 'r') as csv_file:
                midi_data = csvmidi.parse(csv_file)
            with open(output_file, 'wb') as midi_file:
                writer = FileWriter(midi_file)
                writer.write(midi_data)
            print(f"Successfully converted to {output_file}")
            
    except Exception as e:
        print(f"Error during conversion: {str(e)}")

if __name__ == "__main__":
    main()
