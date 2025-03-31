"""
Entry point for running the MusicMidi application.
Follows a simple workflow:
1. Load song from input/songs
2. Parse song data
3. Generate patterns for each instrument
4. Create MIDI files
5. Generate output and logs
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
print(f"Project root: {project_root}")
sys.path.append(str(project_root))

from src.core.song_parser import parse_song_file, SongData
from src.core.midi_generator import MIDIGenerator
from src.instruments.piano import Piano
from src.instruments.guitar import Guitar
from src.instruments.bass import Bass
from src.instruments.drums import Drums

def get_available_songs(songs_dir: Path) -> list[Path]:
    """Get a list of available song files."""
    print(f"Looking for songs in: {songs_dir}")
    songs = list(songs_dir.glob("*.txt"))
    print(f"Found songs: {[s.name for s in songs]}")
    return songs

def select_song(songs: List[Path], song_number: Optional[int] = None) -> Path:
    """Let user select a song or auto-select based on number.
    
    Args:
        songs: List of available song files
        song_number: Optional song number to select (1-based index)
        
    Returns:
        Selected song file path
    """
    # Print available songs
    print("\nAvailable songs:")
    for i, song in enumerate(songs, 1):
        print(f"{i}. {song.stem}")
    
    # If song number provided and valid, use it
    if song_number is not None:
        if 1 <= song_number <= len(songs):
            selected_song = songs[song_number - 1]
            print(f"\nSelected song {song_number}: {selected_song.stem}")
            return selected_song
        else:
            print(f"\nInvalid song number {song_number}. Auto-selecting song 3.")
    
    # Default to song 3 (Piano_test)
    selected_song = songs[2]
    print(f"\nAuto-selecting song 3: {selected_song.stem}")
    return selected_song

def log_generation(song_data, instruments, patterns, output_dir: Path):
    """Log the generation process and results."""
    log_file = output_dir / "Output-Text" / f"{song_data.title.replace(' ', '_')}_log.txt"
    
    with open(log_file, 'w') as f:
        f.write(f"MIDI Generation Log for: {song_data.title}\n")
        f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("Song Information:\n")
        f.write(f"Title: {song_data.title}\n")
        f.write(f"Tempo: {song_data.tempo} BPM\n")
        f.write(f"Time Signature: {song_data.time_signature}\n")
        f.write(f"Key: {song_data.key}\n")
        f.write(f"Genre: {song_data.genre}\n\n")
        
        f.write("Generated Patterns:\n")
        for instrument, pattern in zip(instruments, patterns):
            f.write(f"\n{instrument.__class__.__name__} (Channel {instrument.midi_channel}):\n")
            for note_event in pattern:
                f.write(f"  {note_event}\n")

def process_song(song_file: Path) -> None:
    """Process a song file and generate MIDI output.
    
    Args:
        song_file: Path to the song file
    """
    try:
        print(f"\nParsing song file: {song_file.name}\n")
        
        # Parse song file
        song_data = parse_song_file(song_file)
        
        # Validate song data
        if not song_data.title or not song_data.tempo or not song_data.time_signature or not song_data.key:
            raise ValueError(f"Missing required song information in {song_file.name}. " +
                          "Please ensure title, tempo, time signature, and key are specified.")
        
        if song_data.tempo <= 0:
            raise ValueError(f"Invalid tempo {song_data.tempo} in {song_file.name}. Tempo must be positive.")
        
        if song_data.tempo < 40 or song_data.tempo > 208:
            raise ValueError(f"Tempo {song_data.tempo} BPM in {song_file.name} is outside supported range (40-208 BPM).")
        
        # Create output directory
        output_dir = project_root / "output"
        output_dir.mkdir(exist_ok=True)
        (output_dir / "Output-Text").mkdir(exist_ok=True)
        
        # Generate main MIDI file
        print("Generating MIDI file for {}...".format(song_file.stem))
        midi_gen = MIDIGenerator(
            tempo=song_data.tempo,
            time_signature=song_data.time_signature
        )
        
        # Write main MIDI file
        output_file = output_dir / f"{song_file.stem}.mid"
        midi_gen.write(str(output_file))
        print(f"Generated MIDI file: {output_file}")
        
        # Initialize instruments
        instruments = [
            Piano(midi_channel=0),
            Guitar(midi_channel=1),
            Bass(midi_channel=2),
            Drums(midi_channel=9)
        ]
        
        # Generate patterns for each instrument
        patterns = []
        for instrument in instruments:
            print(f"\nGenerating pattern for {instrument.__class__.__name__}...")
            
            # Get the first chord from the song data
            chord = "C"  # Default to C if no chord specified
            if song_data.notes:
                first_note = song_data.notes[0]['note']
                if first_note.startswith('['):
                    # Extract chord from first chord notation
                    chord = first_note.strip('[]').split(',')[0][0]  # Take first note of chord
            
            try:
                # Generate pattern using song data
                pattern = instrument.generate_pattern(
                    chord=chord,
                    style=song_data.genre,
                    song_data=song_data
                )
                patterns.append(pattern)
                
                # Create MIDI file for this instrument
                midi_gen = MIDIGenerator(
                    tempo=song_data.tempo,
                    time_signature=song_data.time_signature
                )
                midi_gen.add_pattern(instrument, pattern)
                
                # Write individual MIDI file
                output_file = output_dir / f"{song_data.title.replace(' ', '_')}_{instrument.__class__.__name__.lower()}.mid"
                midi_gen.write(str(output_file))
                print(f"Generated MIDI file: {output_file}")
                
                # Cleanup
                midi_gen.cleanup()
            except ValueError as e:
                print(f"Warning: Could not generate pattern for {instrument.__class__.__name__}: {str(e)}")
                continue
        
        # Step 5: Generate log file
        log_generation(song_data, instruments, patterns, output_dir)
        log_file = output_dir / "Output-Text" / f"{song_data.title.replace(' ', '_')}_log.txt"
        print(f"\nGenerated log file: {log_file}")
        
        # Cleanup instruments
        for instrument in instruments:
            instrument.cleanup()
            
    except ValueError as e:
        print(f"Error processing {song_file}: {str(e)}")
        print("\nSkipping to next available song...")
        return
    except Exception as e:
        print(f"Error processing {song_file}: {str(e)}")
        raise

def main():
    """Main entry point for the MusicMidi application."""
    try:
        print("MusicMidi - MIDI Music Generator")
        print("================================\n")
        
        # Get input song file
        songs_dir = project_root / "input" / "songs"
        if not songs_dir.exists():
            print(f"Error: Songs directory not found at {songs_dir}")
            return
        
        # Let user select a song
        songs = get_available_songs(songs_dir)
        if not songs:
            print(f"Error: No song files found in {songs_dir}")
            return
            
        print(f"Found {len(songs)} song files")
        
        # Get song number from command line argument if provided
        song_number = None
        if len(sys.argv) > 1:
            try:
                song_number = int(sys.argv[1])
            except ValueError:
                print(f"Invalid song number: {sys.argv[1]}")
        
        selected_song = select_song(songs, song_number)
        
        # Process the selected song
        process_song(selected_song)
        
        print("\nProcessing complete!")
        
    except Exception as e:
        print(f"\nError in main: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main()) 