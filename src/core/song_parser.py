"""Song file parsing module."""

from dataclasses import dataclass
from typing import List, Tuple, Dict
from pathlib import Path

@dataclass
class Section:
    """Represents a section in a song."""
    name: str
    start_time: float
    end_time: float
    style: str = "classical"  # Default style for the section
    comments: str = ""  # Section comments/description

@dataclass
class SongData:
    """Represents the parsed data from a song file."""
    title: str
    tempo: int
    time_signature: Tuple[int, int]
    key: str
    genre: str = "classical"
    notes: List[Dict] = None  # List of note events with timing, duration, etc.
    sections: List[Section] = None  # List of sections in the song

def normalize_key(key: str) -> str:
    """Normalize key format to standard form.
    
    Args:
        key: Key string in various formats (e.g., "E minor", "Em", "e minor")
        
    Returns:
        Normalized key string (e.g., "E minor")
    """
    key = key.strip().lower()
    
    # Handle common key formats
    if key.endswith('m'):  # e.g., "Em"
        return f"{key[0].upper()} minor"
    elif 'minor' in key:  # e.g., "e minor"
        return f"{key[0].upper()} minor"
    elif 'major' in key:  # e.g., "E major"
        return f"{key[0].upper()} major"
    else:  # Assume major if not specified
        return f"{key[0].upper()} major"

def parse_song_file(file_path: Path) -> SongData:
    """Parse a song file and return its data.
    
    Args:
        file_path: Path to the song file
        
    Returns:
        SongData object containing the parsed song information
        
    Raises:
        ValueError: If the file format is invalid
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Initialize default values
    title = ""
    tempo = 120
    time_signature = (4, 4)
    key = "C major"
    genre = "classical"
    notes = []
    sections = []
    current_section = None
    current_comments = []
    
    # Parse header information and notes
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('#'):
            # Collect comments for the current section
            comment = line[1:].strip()
            if comment:
                current_comments.append(comment)
            continue
            
        if line.startswith('[') and line.endswith(']'):
            # Parse section marker
            section_info = line[1:-1].strip()
            if ':' in section_info:
                section_name, style = section_info.split(':', 1)
                section_name = section_name.strip()
                style = style.strip()
            else:
                section_name = section_info
                style = genre  # Use song's genre as default
                
            # If we have a previous section, set its end time
            if current_section:
                current_section.end_time = float(notes[-1]['time']) + float(notes[-1]['duration'])
                sections.append(current_section)
            
            # Start new section
            current_section = Section(
                name=section_name,
                start_time=float(notes[-1]['time']) if notes else 0.0,
                end_time=0.0,  # Will be set when next section starts or at end
                style=style,
                comments=" ".join(current_comments)  # Join collected comments
            )
            current_comments = []  # Reset comments for new section
            continue
            
        if ':' in line:
            # Parse metadata
            key_name, value = line.split(':', 1)
            key_name = key_name.strip()
            value = value.strip()
            
            # Remove any comments
            if '#' in value:
                value = value.split('#')[0].strip()
            
            if key_name == "Title":
                title = value
            elif key_name == "Tempo":
                try:
                    tempo = int(value)
                    if tempo <= 0:
                        raise ValueError(f"Tempo must be positive: {value}")
                except ValueError:
                    raise ValueError(f"Invalid tempo value: {value}")
            elif key_name == "Time Signature":
                try:
                    num, den = value.split('/')
                    time_signature = (int(num), int(den))
                except ValueError:
                    raise ValueError(f"Invalid time signature: {value}")
            elif key_name == "Key":
                key = normalize_key(value)
            elif key_name == "Genre":
                genre = value.lower()
        
        elif '|' in line:
            # Parse note information in format: time|duration|dynamic|note
            try:
                # Remove any comments from the line
                if '#' in line:
                    line = line.split('#')[0].strip()
                
                time, duration, dynamic, note = line.split('|')
                
                note_info = {
                    'time': float(time),
                    'note': note.strip(),
                    'dynamic': dynamic.strip(),
                    'duration': duration.strip()
                }
                notes.append(note_info)
                
            except (ValueError, IndexError) as e:
                print(f"Warning: Skipping invalid line: {line}")
                continue
    
    # Add the final section if we have one
    if current_section and notes:
        current_section.end_time = float(notes[-1]['time']) + float(notes[-1]['duration'])
        sections.append(current_section)
    
    if not title:
        title = file_path.stem
    
    return SongData(
        title=title,
        tempo=tempo,
        time_signature=time_signature,
        key=key,
        genre=genre,
        notes=notes,
        sections=sections
    ) 