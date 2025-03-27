from midiutil import MIDIFile
import os
import re
from pathlib import Path
from datetime import datetime
import random
from genre_manager import GenreManager
import argparse
import sys
import math
import traceback

class MusicTheory:
    """Music theory tools to ensure proper chord selection and progression"""
    
    def __init__(self):
        # Major and minor scales (intervals from root)
        self.scales = {
            'major': [0, 2, 4, 5, 7, 9, 11],  # C, D, E, F, G, A, B
            'minor': [0, 2, 3, 5, 7, 8, 10]   # C, D, Eb, F, G, Ab, Bb
        }
        
        # Chord types by scale degree (for major keys)
        # Using Roman numeral notation: I, ii, iii, IV, V, vi, vii°
        self.major_degree_chords = {
            0: 'major',      # I
            1: 'minor',      # ii
            2: 'minor',      # iii
            3: 'major',      # IV
            4: 'major',      # V
            5: 'minor',      # vi
            6: 'diminished'  # vii°
        }
        
        # Chord types by scale degree (for minor keys)
        # Using Roman numeral notation: i, ii°, III, iv, v, VI, VII
        self.minor_degree_chords = {
            0: 'minor',      # i
            1: 'diminished', # ii°
            2: 'major',      # III
            3: 'minor',      # iv
            4: 'minor',      # v (or major V in harmonic minor)
            5: 'major',      # VI
            6: 'major'       # VII
        }
        
        # Chord intervals by chord type
        self.chord_types = {
            'major': [0, 4, 7],         # Root, major 3rd, perfect 5th
            'minor': [0, 3, 7],         # Root, minor 3rd, perfect 5th
            'diminished': [0, 3, 6],    # Root, minor 3rd, diminished 5th
            'augmented': [0, 4, 8],     # Root, major 3rd, augmented 5th
            'dominant7': [0, 4, 7, 10], # Root, major 3rd, perfect 5th, minor 7th
            'major7': [0, 4, 7, 11],    # Root, major 3rd, perfect 5th, major 7th
            'minor7': [0, 3, 7, 10]     # Root, minor 3rd, perfect 5th, minor 7th
        }
        
        # Common chord progressions by scale degree (using index 0-6)
        self.chord_progressions = {
            'basic': [0, 4, 5, 0],      # I-V-vi-I
            'pop': [0, 4, 5, 3],        # I-V-vi-IV
            'classical': [0, 3, 4, 0],  # I-IV-V-I
            'jazz': [1, 4, 0, 5],       # ii-V-I-vi
            'blues': [0, 0, 0, 0, 3, 3, 0, 0, 4, 3, 0, 0]  # I-I-I-I-IV-IV-I-I-V-IV-I-I
        }
        
        # Strong chord relationships - chords that sound good after each other
        # Each chord can be followed by these scale degrees
        self.chord_relationships = {
            0: [1, 2, 3, 4, 5, 6],  # I can go to any
            1: [0, 2, 4],           # ii often goes to V or I
            2: [0, 3, 5],           # iii often goes to vi or IV
            3: [0, 1, 4, 6],        # IV often goes to I or V
            4: [0, 3, 5],           # V often goes to I
            5: [1, 3, 4],           # vi often goes to ii or IV
            6: [0]                  # vii° often goes to I
        }
    
    def get_note_in_scale(self, note, key, scale_type='major'):
        """Check if a note belongs to the given scale"""
        # Normalize note and key to 0-11 range (C=0, B=11)
        note_class = note % 12
        key_class = key % 12
        
        # Get the scale intervals
        scale_intervals = self.scales[scale_type]
        
        # Calculate the relative position of the note in the key's scale
        for interval in scale_intervals:
            if (key_class + interval) % 12 == note_class:
                # Return the scale degree (0-6)
                return scale_intervals.index(interval)
        
        return None  # Note is not in the scale
    
    def get_chord_for_note(self, note, key, scale_type='major'):
        """Get appropriate chord for a note in the given key"""
        # Find the scale degree of the note
        scale_degree = self.get_note_in_scale(note, key, scale_type)
        
        # If note is not in scale, use the closest scale note
        if scale_degree is None:
            # Find the closest note in the scale
            scale = [(key + interval) % 12 for interval in self.scales[scale_type]]
            distances = [(note - scale_note) % 12 for scale_note in scale]
            min_distance_index = distances.index(min(distances))
            scale_degree = min_distance_index
        
        # Get the chord type for this scale degree
        if scale_type == 'major':
            chord_type = self.major_degree_chords[scale_degree]
        else:
            chord_type = self.minor_degree_chords[scale_degree]
        
        # Get the chord intervals
        chord_intervals = self.chord_types[chord_type]
        
        # Calculate the root note of the chord based on scale degree
        scale = self.scales[scale_type]
        root_offset = scale[scale_degree]
        root_note = (key + root_offset) % 12
        
        # Build the full chord
        chord = [(root_note + interval) % 12 for interval in chord_intervals]
        
        return {
            'root': root_note,
            'type': chord_type,
            'notes': chord,
            'scale_degree': scale_degree
        }
    
    def get_suitable_chord_progression(self, melody_notes, key, scale_type='major', measures=4):
        """Generate a suitable chord progression for a melody"""
        # Get the predominant notes at the start of each measure
        measure_notes = []
        current_measure = 0
        
        # Group notes by measure
        for note in melody_notes:
            measure = int(note['start'] // 4)
            if measure >= len(measure_notes):
                # Add empty lists for any skipped measures
                while len(measure_notes) <= measure:
                    measure_notes.append([])
            
            # Add the note to its measure
            measure_notes[measure].append(note['pitch'] % 12)
        
        # Ensure we have enough measures
        while len(measure_notes) < measures:
            measure_notes.append([])
        
        # Get the most common note in each measure
        representative_notes = []
        for measure in measure_notes:
            if not measure:
                # Use the tonic if no notes in the measure
                representative_notes.append(key % 12)
                continue
                
            # Count occurrences of each note
            note_counts = {}
            for note in measure:
                note_counts[note] = note_counts.get(note, 0) + 1
            
            # Get the most common note
            most_common = max(note_counts, key=note_counts.get)
            representative_notes.append(most_common)
        
        # Generate appropriate chords for each measure
        chord_progression = []
        prev_chord_degree = None
        
        for note in representative_notes:
            # Get suitable chord
            chord = self.get_chord_for_note(note, key, scale_type)
            
            # Check if we need to find a more suitable chord based on progression
            if prev_chord_degree is not None:
                # If current chord doesn't have a strong relationship with previous
                if chord['scale_degree'] not in self.chord_relationships.get(prev_chord_degree, []):
                    # Look for alternative chords that contain the note
                    for degree in self.chord_relationships[prev_chord_degree]:
                        alt_chord = self.get_chord_for_scale_degree(degree, key, scale_type)
                        # Check if the melody note is in this chord
                        if note % 12 in alt_chord['notes']:
                            chord = alt_chord
                            break
            
            chord_progression.append(chord)
            prev_chord_degree = chord['scale_degree']
        
        return chord_progression
    
    def get_chord_for_scale_degree(self, degree, key, scale_type='major'):
        """Get the chord for a specific scale degree in the given key"""
        # Get the chord type for this scale degree
        if scale_type == 'major':
            chord_type = self.major_degree_chords[degree]
        else:
            chord_type = self.minor_degree_chords[degree]
        
        # Get the chord intervals
        chord_intervals = self.chord_types[chord_type]
        
        # Calculate the root note of the chord based on scale degree
        scale = self.scales[scale_type]
        root_offset = scale[degree]
        root_note = (key + root_offset) % 12
        
        # Build the full chord
        chord = [(root_note + interval) % 12 for interval in chord_intervals]
        
        return {
            'root': root_note,
            'type': chord_type,
            'notes': chord,
            'scale_degree': degree
        }

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

    def create_midi_file(self, song_data, output_path, tempo=120, enable_accompaniment=False, accompaniment_style='basic'):
        """Create a MIDI file from song data with optional accompaniment"""
        try:
            print(f"\nCreating MIDI file: {output_path}")
            print(f"Tempo: {tempo}")
            print(f"Number of measures: {len(song_data['measures'])}")
            print(f"Accompaniment: {'Enabled (' + accompaniment_style + ')' if enable_accompaniment else 'Disabled'}")
            
            # Determine number of tracks
            num_tracks = 2 if enable_accompaniment else 1
            
            # Create a MIDI file with one or two tracks
            midi = MIDIFile(num_tracks, adjust_origin=True)
            
            # Set the tempo for all tracks
            midi.addTempo(0, 0, tempo)
            if enable_accompaniment:
                midi.addTempo(1, 0, tempo)
            
            # Track 0: Melody
            # Add notes to the melody track
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
            
            # Track 1: Accompaniment (if enabled)
            if enable_accompaniment:
                print("\nGenerating accompaniment...")
                
                # Create accompaniment generator
                accompaniment_gen = AccompanimentGenerator()
                
                # Generate accompaniment based on melody
                accompaniment_data = accompaniment_gen.generate_accompaniment(song_data, style=accompaniment_style)
                
                # Add accompaniment notes to the track
                current_time = 0
                accompaniment_notes = 0
                
                for measure_num, measure in enumerate(accompaniment_data, 1):
                    print(f"Processing accompaniment for measure {measure_num}")
                    
                    # Process each note in the accompaniment measure
                    for note_data in measure:
                        note_start = current_time + note_data['start']
                        
                        # Ensure all values are within valid MIDI ranges
                        pitch_value = max(0, min(127, note_data['pitch']))
                        velocity = max(0, min(127, note_data['velocity']))
                        duration = max(0.1, note_data['duration'])
                        
                        midi.addNote(1, 0, pitch_value, note_start, duration, velocity)
                        accompaniment_notes += 1
                    
                    # Move to next measure
                    current_time += 4.0  # Assuming 4/4 time signature
                
                print(f"Added {accompaniment_notes} accompaniment notes")
                total_notes += accompaniment_notes
            
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

class AccompanimentGenerator:
    """Generates accompaniment patterns based on melody notes"""
    
    def __init__(self):
        # Define common chord patterns in root position
        self.chord_patterns = {
            'basic': [0, 4, 7],         # Basic triad (1-3-5)
            'seventh': [0, 4, 7, 10],   # Seventh chord (1-3-5-7)
            'open': [0, 7, 12],         # Open fifth with octave (1-5-8)
            'sus4': [0, 5, 7],          # Suspended 4th (1-4-5)
            'add9': [0, 4, 7, 14]       # Add9 chord (1-3-5-9)
        }
        
        # Common accompaniment patterns
        self.rhythm_patterns = {
            'whole': [[0.0, 4.0]],  # Single whole note
            'half': [[0.0, 2.0], [2.0, 2.0]],  # Two half notes
            'quarter': [[0.0, 1.0], [1.0, 1.0], [2.0, 1.0], [3.0, 1.0]],  # Four quarter notes
            'waltz': [[0.0, 1.0], [1.0, 1.0], [2.0, 1.0], [3.0, 1.0]],  # Basic 4/4 waltz pattern
            'arpeggio': [[0.0, 0.5], [0.5, 0.5], [1.0, 0.5], [1.5, 0.5], 
                        [2.0, 0.5], [2.5, 0.5], [3.0, 0.5], [3.5, 0.5]],  # Eighth note arpeggio
            'alberti': [[0.0, 0.5], [0.5, 0.5], [1.0, 0.5], [1.5, 0.5],
                       [2.0, 0.5], [2.5, 0.5], [3.0, 0.5], [3.5, 0.5]]  # Alberti bass pattern
        }
        
        # Map note names to scale degrees (for key detection)
        self.note_to_degree = {
            'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11
        }
        
        # Create music theory helper
        self.music_theory = MusicTheory()
        
        # Initialize genre manager
        self.genre_manager = GenreManager()
    
    def detect_key(self, song_data):
        """Attempts to detect the key from the melody notes or metadata"""
        # First check if key is specified in metadata
        if 'key' in song_data and song_data['key']:
            key_str = song_data['key'].strip()
            # Extract just the note portion (ignoring major/minor)
            key_match = re.match(r'([A-G][#b]?)\s*(major|minor|maj|min)?', key_str, re.IGNORECASE)
            if key_match:
                root_note = key_match.group(1)
                # Convert key to MIDI note number (using C4 as reference)
                if root_note in self.note_to_degree:
                    return self.note_to_degree[root_note]
        
        # If no key specified, try to detect from notes
        # This is a simple approach - count note occurrences and find the most common
        notes = []
        for measure in song_data['measures']:
            for note_data in measure:
                if isinstance(note_data, list):  # Chord
                    for note in note_data:
                        notes.append(note['pitch'] % 12)  # Use mod 12 to get pitch class
                else:  # Single note
                    notes.append(note_data['pitch'] % 12)
        
        if not notes:
            return 0  # Default to C if no notes
            
        # Find most common note (simple heuristic for key detection)
        note_counts = {}
        for note in notes:
            note_counts[note] = note_counts.get(note, 0) + 1
        
        # Return the most common note as the key
        if note_counts:
            return max(note_counts, key=note_counts.get)
        return 0  # Default to C if no notes
    
    def detect_scale_type(self, song_data, key):
        """Determines if the song is in a major or minor key"""
        # Check if scale type is specified in metadata
        if 'key' in song_data and song_data['key']:
            key_str = song_data['key'].strip().lower()
            if 'minor' in key_str or 'min' in key_str:
                return 'minor'
            else:
                return 'major'  # Default to major if not specified
        
        # Count notes that match major vs minor scale
        major_count = 0
        minor_count = 0
        
        # Get all the notes from the song
        all_notes = []
        for measure in song_data['measures']:
            for note_data in measure:
                if isinstance(note_data, list):  # Chord
                    for note in note_data:
                        all_notes.append(note['pitch'] % 12)
                else:  # Single note
                    all_notes.append(note_data['pitch'] % 12)
        
        # Check how many notes fit in each scale
        for note in all_notes:
            # Check if note is in major scale
            if self.music_theory.get_note_in_scale(note, key, 'major') is not None:
                major_count += 1
            
            # Check if note is in minor scale
            if self.music_theory.get_note_in_scale(note, key, 'minor') is not None:
                minor_count += 1
        
        # Return the scale type that matches more notes
        return 'minor' if minor_count > major_count else 'major'
    
    def generate_chord_progression(self, song_data, key, scale_type='major'):
        """Generate a chord progression based on melody notes and music theory"""
        # Flatten the measures into a single list of notes
        all_notes = []
        for measure in song_data['measures']:
            for note_data in measure:
                if isinstance(note_data, list):  # Chord
                    for note in note_data:
                        all_notes.append(note)
                else:  # Single note
                    all_notes.append(note_data)
        
        # Get a suitable chord progression from the music theory helper
        return self.music_theory.get_suitable_chord_progression(
            all_notes, 
            key, 
            scale_type, 
            measures=len(song_data['measures'])
        )
    
    def build_chord_notes(self, chord, octave=3):
        """Convert a chord dictionary to MIDI note numbers in a specific octave"""
        base_note = octave * 12
        midi_notes = []
        
        for note in chord['notes']:
            midi_notes.append(base_note + note)
        
        return midi_notes
    
    def generate_accompaniment(self, song_data, style='basic', genre_id='classical'):
        """Generate accompaniment based on melody, chosen style, and genre"""
        # Detect the song key and scale type
        key = self.detect_key(song_data)
        scale_type = self.detect_scale_type(song_data, key)
        
        print(f"Detected key: {key}, Scale type: {scale_type}, Genre: {genre_id}")
        
        # Get the genre
        genre = self.genre_manager.get_genre(genre_id)
        
        # Get the rhythm pattern based on style or genre
        if style == 'genre':
            # Use the genre's preferred accompaniment pattern
            pattern_type = genre.get_accompaniment_pattern()
            rhythm = genre.get_rhythm_pattern(pattern_type)
            print(f"Using genre-specific '{pattern_type}' pattern")
        else:
            # Use the specified style
            if style in self.rhythm_patterns:
                rhythm = self.rhythm_patterns[style]
            else:
                rhythm = self.rhythm_patterns['quarter']  # Default
            print(f"Using specified '{style}' pattern")
        
        # Generate a chord progression based on music theory
        chord_progression = self.generate_chord_progression(song_data, key, scale_type)
        
        # Use genre-specific chord progressions if using genre style
        if style == 'genre' and genre.chord_progressions:
            # Override with a genre-specific chord progression
            progression_length = len(song_data['measures'])
            genre_progression = genre.get_chord_progression(progression_length)
            # Map scale degrees to actual chords
            genre_chords = []
            for degree in genre_progression:
                genre_chords.append(self.music_theory.get_chord_for_scale_degree(degree, key, scale_type))
            
            # Use the genre progression if it's long enough
            if len(genre_chords) >= progression_length:
                chord_progression = genre_chords[:progression_length]
                print(f"Using genre-specific chord progression")
        
        # Generate accompaniment for each measure
        accompaniment = []
        
        for measure_idx, measure in enumerate(song_data['measures']):
            measure_notes = []
            
            # Skip empty measures
            if not measure:
                accompaniment.append([])
                continue
                
            # Get the chord for this measure
            if measure_idx < len(chord_progression):
                chord = chord_progression[measure_idx]
            else:
                # If we don't have enough chords, repeat the last one or use I
                chord = chord_progression[-1] if chord_progression else self.music_theory.get_chord_for_scale_degree(0, key, scale_type)
            
            # Convert chord to actual MIDI notes (in bass register)
            # Start 2 octaves below middle C for bass
            chord_notes = self.build_chord_notes(chord, octave=2)
            
            print(f"Measure {measure_idx+1}: Chord {chord['type']} (Scale degree: {chord['scale_degree']})")
            
            # Get the velocity based on genre dynamics
            if style == 'genre':
                velocity = self.get_velocity_for_genre(genre)
            else:
                velocity = 60  # Default medium-soft for arpeggiated patterns
                if style not in ['arpeggio', 'alberti']:
                    velocity = 50  # Softer for block chord patterns
            
            # Apply the rhythm pattern
            for start, duration in rhythm:
                # For arpeggio and alberti patterns, choose different chord notes
                if style in ['arpeggio', 'alberti'] or (style == 'genre' and pattern_type in ['arpeggio', 'alberti', 'walking', 'swing']):
                    # Skip if no chord notes available
                    if not chord_notes:
                        continue
                    
                    # For arpeggio/walking bass, cycle through chord notes
                    if style == 'arpeggio' or (style == 'genre' and pattern_type in ['arpeggio', 'walking']):
                        index = int(start * 2) % len(chord_notes)
                        pitch = chord_notes[index]
                    # For alberti, use pattern: lowest, highest, middle, highest
                    elif style == 'alberti' or (style == 'genre' and pattern_type == 'alberti'):
                        if len(chord_notes) >= 3:
                            pattern_idx = int(start * 2) % 4
                            if pattern_idx == 0:
                                pitch = chord_notes[0]  # Lowest
                            elif pattern_idx == 1:
                                pitch = chord_notes[-1]  # Highest
                            elif pattern_idx == 2:
                                pitch = chord_notes[len(chord_notes)//2]  # Middle
                            else:
                                pitch = chord_notes[-1]  # Highest
                        else:
                            # If chord has fewer than 3 notes, just alternate
                            if not chord_notes:
                                continue
                            pitch = chord_notes[int(start * 2) % len(chord_notes)]
                    # For swing, use a walking bass with slight swing feel
                    elif style == 'genre' and pattern_type == 'swing':
                        index = int(start * 2) % len(chord_notes)
                        pitch = chord_notes[index]
                        # Add slight swing feel
                        if start % 1 == 0:  # On the beat
                            velocity += 5  # Accent on-beat notes
                    
                    # Add the single note
                    measure_notes.append({
                        'pitch': pitch,
                        'duration': duration,
                        'velocity': velocity,
                        'start': start,
                        'is_chord': False
                    })
                else:
                    # For block chord patterns, use the whole chord
                    for pitch in chord_notes:
                        
                        measure_notes.append({
                            'pitch': pitch,
                            'duration': duration,
                            'velocity': velocity,
                            'start': start,
                            'is_chord': True
                        })
            
            accompaniment.append(measure_notes)
        
        return accompaniment
    
    def get_velocity_for_genre(self, genre):
        """Get appropriate velocity based on genre dynamics"""
        default_dynamic = genre.dynamics.get('default', 'mf')
        variation = genre.dynamics.get('variation', 'low')
        
        # Map dynamics to base velocity
        dynamic_map = {
            'pp': 30,
            'p': 45, 
            'mp': 60,
            'mf': 75,
            'f': 90,
            'ff': 105
        }
        
        # Get base velocity
        base_velocity = dynamic_map.get(default_dynamic, 75)
        
        # Apply variation based on genre characteristics
        if variation == 'high':
            return base_velocity + random.randint(-15, 15)
        elif variation == 'medium':
            return base_velocity + random.randint(-10, 10)
        else:  # low variation
            return base_velocity + random.randint(-5, 5)

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

def process_song(input_file, output_dir, enable_accompaniment=False, accompaniment_style='basic'):
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
    
    # Add accompaniment info to filename if enabled
    if enable_accompaniment:
        filename_base = f"{safe_title}_{accompaniment_style}_accompaniment_{safe_key}"
    else:
        filename_base = f"{safe_title}_melody_only_{safe_key}"
    
    # Get next version number
    version = get_next_version(output_dir, filename_base)
    output_file = os.path.join(output_dir, f"{filename_base}_v{version}.mid")
    
    # Parse the song file
    song_data = parse_song_file(input_file)
    if not song_data:
        print(f"Failed to parse {input_file}")
        return False
    
    # Create MIDI file
    generator = MIDIGenerator()
    return generator.create_midi_file(
        song_data, 
        output_file, 
        song_data['tempo'],
        enable_accompaniment=enable_accompaniment,
        accompaniment_style=accompaniment_style
    )

def process_all_songs(input_dir, output_dir, enable_accompaniment=False, accompaniment_style='basic'):
    """Process all song files in the input directory"""
    success_count = 0
    total_count = 0
    
    for file in os.listdir(input_dir):
        if file.endswith('.txt'):
            total_count += 1
            input_file = os.path.join(input_dir, file)
            if process_song(input_file, output_dir, enable_accompaniment, accompaniment_style):
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

def generate_midi(song_data, output_file=None, accompaniment_style='basic', genre=None):
    """Generate a MIDI file from the song data dictionary"""
    # Set up MIDI file with 2 tracks (melody and accompaniment)
    midi = MIDIFile(2)
    
    # Track names
    track_names = ["Melody", "Accompaniment"]
    
    # Create default time signature (4/4)
    time_signature = song_data.get('time_signature', '4/4')
    numerator, denominator = map(int, time_signature.split('/'))
    
    # Set up tracks
    for i, name in enumerate(track_names):
        midi.addTrackName(i, 0, name)
        midi.addTimeSignature(i, 0, numerator, int(math.log(denominator, 2)), 24)
        
        # Set tempo (default to 120 BPM if not specified)
        tempo = int(song_data.get('tempo', 120))
        midi.addTempo(i, 0, tempo)
    
    # Track 0: Melody
    # Set instrument for melody (default to piano)
    melody_instrument = int(song_data.get('instrument', 0))  # 0 = Acoustic Grand Piano
    midi.addProgramChange(0, 0, 0, melody_instrument)
    
    # Generate MIDI data for each measure in the melody
    time = 0  # Current time in quarter notes
    
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
                    # Extract note data
                    pitch = note.get('pitch', 60)
                    duration = note.get('duration', 1.0)
                    # Normalize velocity to a maximum of 100
                    velocity = int(min(100, (note.get('velocity', 90) / max_velocity) * 100))
                    
                    # Add note to MIDI file
                    midi.addNote(0, 0, pitch, chord_start, duration, velocity)
                    measure_end_time = max(measure_end_time, chord_start + duration)
            else:  # Single note
                # Extract note data
                pitch = note_data.get('pitch', 60)
                duration = note_data.get('duration', 1.0)
                start = note_data.get('start', 0) + time
                # Normalize velocity
                velocity = int(min(100, (note_data.get('velocity', 90) / max_velocity) * 100))
                
                # Add note to MIDI file
                midi.addNote(0, 0, pitch, start, duration, velocity)
                measure_end_time = max(measure_end_time, start + duration)
        
        # Update the time to the end of the measure
        time = measure_end_time
    
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
                # Set the accompaniment instrument
                midi.addProgramChange(1, 0, 0, instrument)
                print(f"Using genre-specific instrument: {instrument}")
            else:
                # Default to acoustic bass
                midi.addProgramChange(1, 0, 0, 32)  # Acoustic Bass
        else:
            # Default to acoustic bass
            midi.addProgramChange(1, 0, 0, 32)  # Acoustic Bass
        
        # Generate accompaniment
        accompaniment = accompaniment_generator.generate_accompaniment(
            song_data, 
            style=accompaniment_style,
            genre_id=genre_id
        )
        
        # Add accompaniment notes to MIDI file
        time = 0
        for measure_idx, measure in enumerate(accompaniment):
            # Skip empty measures
            if not measure:
                # Find the corresponding melody measure duration
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
                # Extract note data
                pitch = note_data.get('pitch', 48)  # Default to C3
                duration = note_data.get('duration', 1.0)
                start = note_data.get('start', 0) + time
                velocity = note_data.get('velocity', 70)  # Accompaniment slightly softer
                
                # Add note to MIDI file
                midi.addNote(1, 0, pitch, start, duration, velocity)
                measure_end_time = max(measure_end_time, start + duration)
            
            # Update the time to the end of the measure
            time = measure_end_time
    
    # Determine output file name if not provided
    if output_file is None:
        # Create a directory for output files if it doesn't exist
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        
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
        
        output_file = output_dir / filename
    
    # Write the MIDI file
    with open(output_file, 'wb') as output_file_obj:
        midi.writeFile(output_file_obj)
    
    return output_file

def main():
    """Process input file and generate MIDI output"""
    parser = argparse.ArgumentParser(description='Convert text-based music notation to MIDI')
    parser.add_argument('input_file', help='Input file with text-based music notation')
    parser.add_argument('-o', '--output', help='Output MIDI file name')
    parser.add_argument('-a', '--accompaniment', 
                        choices=['none', 'basic', 'quarter', 'half', 'whole', 'waltz', 'alberti', 'arpeggio', 'genre'],
                        default='basic',
                        help='Accompaniment style to generate')
    parser.add_argument('-g', '--genre',
                        choices=['classical', 'baroque', 'romantic', 'pop', 'rock', 'jazz', 'swing'],
                        help='Musical genre for the accompaniment')
    
    args = parser.parse_args()
    
    try:
        # Read and parse the input file
        with open(args.input_file, 'r') as file:
            lines = file.readlines()
        
        # Parse the song
        song_data = parse_song(lines)
        
        # Generate MIDI file
        output_file = generate_midi(
            song_data, 
            output_file=args.output,
            accompaniment_style=args.accompaniment,
            genre=args.genre
        )
        
        print(f"MIDI file successfully generated: {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 