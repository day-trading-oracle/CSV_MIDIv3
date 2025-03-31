"""MIDI file generation module."""

import os
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from midiutil import MIDIFile
from ..instruments import BaseInstrument

class MIDIGenerator:
    """Class for generating MIDI files from musical patterns."""
    
    # Standard MIDI program numbers for common instruments (GM Standard)
    MIDI_PROGRAMS = {
        'piano': 0,      # Acoustic Grand Piano
        'guitar': 24,    # Acoustic Guitar (nylon)
        'bass': 32,      # Acoustic Bass
        'drums': 128     # Channel 10 (9 in 0-based) is reserved for percussion
    }
    
    # Standard MIDI drum note mappings (GM Drum Kit)
    DRUM_NOTES = {
        'kick': 36,      # C1 - Bass Drum 1
        'snare': 38,     # D1 - Acoustic Snare
        'hihat': 42,     # F#1 - Closed Hi-Hat
        'hihat_open': 46,  # A#1 - Open Hi-Hat
        'tom1': 45,      # A1 - Low Tom
        'tom2': 47,      # B1 - Mid Tom
        'tom3': 50,      # D2 - High Tom
        'crash': 49,     # C#2 - Crash Cymbal 1
        'ride': 51,      # D#2 - Ride Cymbal 1
        'clap': 39,      # D#1 - Hand Clap
        'rim': 37,       # C#1 - Side Stick
        'cowbell': 56    # G#2 - Cowbell
    }
    
    def __init__(self, tempo: int = 120, time_signature: tuple[int, int] = (4, 4)):
        """Initialize the MIDI generator.
        
        Args:
            tempo: Tempo in beats per minute
            time_signature: Time signature as (numerator, denominator)
        """
        self.tempo = tempo
        self.time_signature = time_signature
        self.midi = MIDIFile(numTracks=1, removeDuplicates=False, deinterleave=False)  # Single track, keep note order
        
        # Set tempo and time signature
        self.midi.addTempo(0, 0, tempo)
        self.midi.addTimeSignature(0, 0, time_signature[0], time_signature[1], 24, 8)
        
        # Track the last note time for each channel
        self._last_note_time = [0.0] * 16
        
        # Store original time signature for conversion
        self._original_time_signature = time_signature
    
    def _convert_time_to_44(self, time: float) -> float:
        """Convert time from original time signature to 4/4.
        
        Args:
            time: Time in beats in original time signature
            
        Returns:
            Time in beats in 4/4 time signature
        """
        if self._original_time_signature == (4, 4):
            return time
            
        # Calculate conversion factor based on time signatures
        original_beats = self._original_time_signature[0]
        original_beat_value = self._original_time_signature[1]
        target_beats = 4
        target_beat_value = 4
        
        # Convert to quarter notes first
        quarter_notes = time * (original_beat_value / 4)
        # Then convert to target time signature
        return quarter_notes * (4 / target_beat_value)
    
    def _quantize_time(self, time: float) -> float:
        """Quantize time to nearest sixteenth note.
        
        Args:
            time: Time in beats
            
        Returns:
            Quantized time in beats
        """
        return round(time * 4) / 4
    
    def _parse_note_event(self, event: Any) -> Optional[Tuple[int, float, float, int]]:
        """Parse a note event into MIDI note, time, duration, and velocity.
        
        Args:
            event: Note event data
            
        Returns:
            Tuple of (note, time, duration, velocity) or None if invalid
        """
        if isinstance(event, tuple) and len(event) >= 3:
            note, time, duration = event[:3]
            velocity = event[3] if len(event) > 3 else 100  # Default velocity if not specified
            if isinstance(note, (int, float)) and isinstance(time, (int, float)) and isinstance(duration, (int, float)):
                return int(note), float(time), float(duration), int(velocity)
        return None
    
    def _get_drum_note(self, drum_type: str) -> int:
        """Get the MIDI note number for a specific drum type.
        
        Args:
            drum_type: Name of the drum (e.g., 'kick', 'snare', 'hihat')
            
        Returns:
            MIDI note number for the drum
        """
        return self.DRUM_NOTES.get(drum_type.lower(), 36)  # Default to kick if not found
    
    def add_pattern(self, instrument: BaseInstrument, pattern: List[Any], 
                   start_time: float = 0.0, duration: float = 1.0) -> None:
        """Add a musical pattern to the MIDI file.
        
        Args:
            instrument: The instrument playing the pattern
            pattern: List of MIDI events (notes, durations, etc.)
            start_time: When to start playing the pattern (in beats)
            duration: How long to play the pattern (in beats)
        """
        if not pattern:
            return
            
        # Get the instrument name and channel
        instrument_name = instrument.__class__.__name__.lower()
        channel = instrument.midi_channel
        
        # Set the instrument program
        if instrument_name in self.MIDI_PROGRAMS:
            program = self.MIDI_PROGRAMS[instrument_name]
            if instrument_name == 'drums':
                # Drums are always on channel 10 (9 in 0-based)
                channel = 9
                program = 0  # Program 0 for drums
            self.midi.addProgramChange(0, channel, 0, program)
        
        # Sort pattern by time to ensure proper note ordering
        sorted_pattern = sorted(pattern, key=lambda x: x[1] if isinstance(x, tuple) and len(x) > 1 else 0)
        
        # Process each event in the pattern
        for event in sorted_pattern:
            note_data = self._parse_note_event(event)
            if note_data:
                note, time, note_duration, velocity = note_data
                
                # Handle drum notes specially
                if instrument_name == 'drums':
                    # If note is a string, it's a drum type name
                    if isinstance(note, str):
                        note = self._get_drum_note(note)
                    # Ensure drum notes are on channel 10 (9 in 0-based)
                    channel = 9
                
                # Ensure valid note range (0-127)
                note = max(0, min(127, note))
                
                # Ensure valid velocity range (0-127)
                velocity = max(0, min(127, velocity))
                
                # Ensure positive duration
                note_duration = max(0.0625, note_duration)  # Minimum 1/16th note
                
                # Convert time to 4/4 if needed
                converted_time = self._convert_time_to_44(start_time + time)
                converted_duration = self._convert_time_to_44(note_duration)
                
                # Quantize the timing
                quantized_time = max(self._last_note_time[channel], 
                                   self._quantize_time(converted_time))
                quantized_duration = self._quantize_time(converted_duration)
                
                # Update last note time for this channel
                self._last_note_time[channel] = quantized_time + quantized_duration
                
                # Add the note with proper timing and velocity
                try:
                    self.midi.addNote(0, channel, note, quantized_time, quantized_duration, velocity)
                except Exception as e:
                    print(f"Warning: Failed to add note {note} at time {quantized_time}: {str(e)}")
                    continue
    
    def write(self, output_path: str) -> None:
        """Write the MIDI file to disk.
        
        Args:
            output_path: Path where to save the MIDI file
        """
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        with open(output_path, 'wb') as f:
            self.midi.writeFile(f)
    
    def cleanup(self) -> None:
        """Clean up any resources used by the MIDI generator."""
        self.midi = None 