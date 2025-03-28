"""
MIDI file generation module.
"""

import math
import os
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
from midiutil import MIDIFile
from .instruments import InstrumentManager, BaseInstrument
from .genre_manager import GenreManager
from .accompaniment_generator import AccompanimentGenerator

def generate_midi(song_data, output_file=None, accompaniment_style='basic', genre=None):
    """Generate a MIDI file from the song data dictionary"""
    try:
        # Validate input data
        if not song_data or 'measures' not in song_data:
            raise ValueError("Invalid song data: missing required fields")
        
        # Set up MIDI file with 3 tracks (melody, accompaniment, and bass)
        midi = MIDIFile(3)
        
        # Track names
        track_names = ["Melody", "Accompaniment", "Bass"]
        
        # Create default time signature (4/4)
        time_signature = song_data.get('time_signature', '4/4')
        numerator, denominator = map(int, time_signature.split('/'))
        
        # Set up tracks with validation
        for i, name in enumerate(track_names):
            midi.addTrackName(i, 0, name)
            midi.addTimeSignature(i, 0, numerator, int(math.log(denominator, 2)), 24)
            
            # Set tempo (default to 120 BPM if not specified)
            tempo = int(song_data.get('tempo', 120))
            if not (20 <= tempo <= 240):  # Valid MIDI tempo range
                tempo = 120
            midi.addTempo(i, 0, tempo)
        
        # Track 0: Melody
        # Set instrument for melody (default to piano)
        melody_instrument = int(song_data.get('instrument', 0))  # 0 = Acoustic Grand Piano
        if not (0 <= melody_instrument <= 127):  # Valid MIDI program range
            melody_instrument = 0
        midi.addProgramChange(0, 0, 0, melody_instrument)
        
        # Generate MIDI data for each measure in the melody
        time = 0  # Current time in quarter notes
        total_notes = 0  # Track number of notes for validation
        
        # Find the highest velocity in the song for normalization
        max_velocity = 0
        for measure in song_data['measures']:
            for note_data in measure:
                if isinstance(note_data, list):  # Chord
                    for note in note_data:
                        max_velocity = max(max_velocity, note.get('velocity', 100))
                else:  # Single note
                    max_velocity = max(max_velocity, note_data.get('velocity', 100))
        
        # If no notes with velocity, default to 100
        if max_velocity == 0:
            max_velocity = 100
        
        # Process each measure
        for measure_idx, measure in enumerate(song_data['measures']):
            measure_start_time = time
            measure_end_time = time
            
            # Process each note in the measure
            for note_data in measure:
                if isinstance(note_data, list):  # Chord
                    # For chords, all notes start at the same time
                    chord_start = note_data[0].get('start', 0) + time
                    
                    for note in note_data:
                        # Extract and validate note data
                        pitch = max(0, min(127, note.get('pitch', 60)))
                        duration = max(0.1, note.get('duration', 1.0))
                        velocity = max(0, min(127, int(min(100, (note.get('velocity', 90) / max_velocity) * 100))))
                        
                        # Add note to MIDI file
                        midi.addNote(0, 0, pitch, chord_start, duration, velocity)
                        total_notes += 1
                        measure_end_time = max(measure_end_time, chord_start + duration)
                else:  # Single note
                    # Extract and validate note data
                    pitch = max(0, min(127, note_data.get('pitch', 60)))
                    duration = max(0.1, note_data.get('duration', 1.0))
                    start = note_data.get('start', 0) + time
                    velocity = max(0, min(127, int(min(100, (note_data.get('velocity', 90) / max_velocity) * 100))))
                    
                    # Add note to MIDI file
                    midi.addNote(0, 0, pitch, start, duration, velocity)
                    total_notes += 1
                    measure_end_time = max(measure_end_time, start + duration)
            
            # Update the time to the end of the measure
            time = measure_end_time
        
        # Validate that we have at least one note
        if total_notes == 0:
            raise ValueError("No valid notes found in the song data")
        
        # Track 1: Accompaniment (if enabled)
        if accompaniment_style != 'none':
            # Generate accompaniment
            genre_id = genre if genre else 'classical'  # Default to classical if not specified
            accompaniment_generator = AccompanimentGenerator()
            
            # Select appropriate bass instrument based on genre
            if genre:
                genre_obj = accompaniment_generator.genre_manager.get_genre(genre)
                if genre_obj:
                    instrument = genre_obj.get_instrument()
                    # Validate instrument number
                    instrument = max(0, min(127, instrument))
                    midi.addProgramChange(1, 0, 0, instrument)
                    print(f"Using genre-specific instrument: {instrument}")
                else:
                    midi.addProgramChange(1, 0, 0, 32)  # Acoustic Bass
            else:
                midi.addProgramChange(1, 0, 0, 32)  # Acoustic Bass
            
            # Generate accompaniment
            accompaniment = accompaniment_generator.generate_accompaniment(
                song_data, 
                style=accompaniment_style,
                genre_id=genre_id
            )
            
            # Add accompaniment notes to MIDI file
            time = 0
            accompaniment_notes = 0
            
            for measure_idx, measure in enumerate(accompaniment):
                # Skip empty measures
                if not measure:
                    if measure_idx < len(song_data['measures']):
                        melody_measure = song_data['measures'][measure_idx]
                        measure_duration = 0
                        for note_data in melody_measure:
                            if isinstance(note_data, list):  # Chord
                                for note in note_data:
                                    measure_duration = max(measure_duration, 
                                                          note.get('start', 0) + note.get('duration', 1.0))
                            else:  # Single note
                                measure_duration = max(measure_duration, 
                                                      note_data.get('start', 0) + note_data.get('duration', 1.0))
                        time += measure_duration
                    else:
                        time += numerator  # Default measure length
                    continue
                
                measure_start_time = time
                measure_end_time = time
                
                # Add notes for this measure
                for note_data in measure:
                    # Extract and validate note data
                    pitch = max(0, min(127, note_data.get('pitch', 48)))  # Default to C3
                    duration = max(0.1, note_data.get('duration', 1.0))
                    start = note_data.get('start', 0) + time
                    velocity = max(0, min(127, note_data.get('velocity', 70)))  # Accompaniment slightly softer
                    
                    # Add note to MIDI file
                    midi.addNote(1, 0, pitch, start, duration, velocity)
                    accompaniment_notes += 1
                    measure_end_time = max(measure_end_time, start + duration)
                
                # Update the time to the end of the measure
                time = measure_end_time
        
        # Track 2: Bass (if enabled)
        if song_data.get('enable_bass', False):
            from .instruments.bass import Bass
            bass = Bass()
            
            # Set bass instrument based on genre
            if genre:
                genre_obj = accompaniment_generator.genre_manager.get_genre(genre)
                if genre_obj:
                    instrument = genre_obj.get_instrument()
                    # Validate instrument number
                    instrument = max(0, min(127, instrument))
                    midi.addProgramChange(2, 0, 0, instrument)
                    print(f"Using genre-specific bass instrument: {instrument}")
                else:
                    midi.addProgramChange(2, 0, 0, 32)  # Acoustic Bass
            else:
                midi.addProgramChange(2, 0, 0, 32)  # Acoustic Bass
            
            # Generate bass pattern
            bass_style = song_data.get('bass_style', 'walking')
            bass_notes = bass.generate_pattern(song_data, style=bass_style, genre=genre)
            
            # Add bass notes to MIDI file
            if bass_notes:  # Only add notes if we have any
                for note_data in bass_notes:
                    try:
                        # Extract and validate note data
                        pitch = max(0, min(127, note_data.get('pitch', 36)))  # Default to C2
                        duration = max(0.1, note_data.get('duration', 1.0))
                        start = note_data.get('start', 0)
                        velocity = max(0, min(127, note_data.get('velocity', 70)))  # Bass slightly softer
                        
                        # Add note to MIDI file
                        midi.addNote(2, 0, pitch, start, duration, velocity)
                    except Exception as e:
                        print(f"Warning: Skipping invalid bass note: {e}")
                        continue
            else:
                print("Warning: No bass notes generated")
                # Add a simple root note as fallback
                midi.addNote(2, 0, 36, 0, 1.0, 70)  # C2, quarter note
        
        # Determine output file name if not provided
        if output_file is None:
            # Create a directory for output files if it doesn't exist
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
            os.makedirs(output_dir, exist_ok=True)
            
            # Use song title for file name, or a timestamp if not available
            title = song_data.get('title', 'Untitled')
            if not title:
                title = 'Untitled'
            
            # Clean filename - remove invalid characters
            title = re.sub(r'[^\w\s-]', '', title.strip().lower())
            title = re.sub(r'[-\s]+', '-', title)
            
            # Add accompaniment style to filename
            filename = f"{title}_{accompaniment_style}"
            
            # Add genre to filename if specified
            if genre:
                filename += f"_{genre}"
            
            # Add timestamp for uniqueness
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename += f"_{timestamp}.mid"
            
            output_file = os.path.join(output_dir, filename)
        
        # Write the MIDI file with validation
        with open(output_file, 'wb') as output_file_obj:
            midi.writeFile(output_file_obj)
        
        # Validate file size
        file_size = os.path.getsize(output_file)
        if file_size < 100:  # MIDI files should be at least 100 bytes
            raise ValueError(f"Generated MIDI file is too small ({file_size} bytes)")
        
        print(f"Successfully generated MIDI file: {output_file}")
        print(f"File size: {file_size} bytes")
        print(f"Total notes: {total_notes}")
        if accompaniment_style != 'none':
            print(f"Accompaniment notes: {accompaniment_notes}")
        if song_data.get('enable_bass', False):
            print(f"Bass notes: {len(bass_notes)}")
        
        return output_file
        
    except Exception as e:
        print(f"Error generating MIDI file: {e}")
        import traceback
        traceback.print_exc()
        return None 