from pathlib import Path
from typing import List, Dict, Optional, Tuple
import random
from dataclasses import dataclass
from enum import Enum, auto

class VariationType(Enum):
    KEY_TRANSPOSITION = auto()
    RHYTHMIC_ALTERATION = auto()
    SCALE_DEGREE_MOD = auto()
    MOOD_ADJUSTMENT = auto()
    TECHNIQUE_VARIATION = auto()
    TIME_SIGNATURE_SHIFT = auto()

@dataclass
class Variation:
    type: VariationType
    original_pattern: str
    modified_pattern: str
    genre: str
    mood: str
    key: str
    technique: Optional[str] = None
    time_signature: str = "4/4"

class VariationManager:
    def __init__(self, variation_patterns_dir: str = "src/patterns/variation_patterns"):
        self.variation_patterns_dir = Path(variation_patterns_dir)
        self.variations: Dict[str, List[Variation]] = {}
        self.load_base_variations()

    def load_base_variations(self) -> None:
        """Load base variations from the variation patterns directory."""
        base_file = self.variation_patterns_dir / "base_variations.txt"
        if not base_file.exists():
            raise FileNotFoundError(f"Base variations file not found at {base_file}")

        # Load and parse base variations
        # Implementation will parse the rules and patterns from base_variations.txt

    def create_variation(self, 
                        pattern: str,
                        instrument: str,
                        genre: str,
                        variation_type: VariationType,
                        mood: Optional[str] = None) -> Optional[Variation]:
        """
        Create a variation of the given pattern based on the specified type.
        
        Args:
            pattern: Original pattern to vary
            instrument: Target instrument (piano, bass, etc.)
            genre: Musical genre
            variation_type: Type of variation to apply
            mood: Optional mood specification
        
        Returns:
            A new Variation object or None if variation cannot be created
        """
        if variation_type == VariationType.KEY_TRANSPOSITION:
            return self._create_key_transposition(pattern, genre, mood or "neutral")
        elif variation_type == VariationType.RHYTHMIC_ALTERATION:
            return self._create_rhythmic_variation(pattern, genre, mood or "neutral")
        elif variation_type == VariationType.SCALE_DEGREE_MOD:
            return self._create_scale_degree_variation(pattern, genre, mood or "neutral")
        elif variation_type == VariationType.MOOD_ADJUSTMENT:
            return self._create_mood_variation(pattern, genre, mood or "neutral")
        elif variation_type == VariationType.TECHNIQUE_VARIATION:
            return self._create_technique_variation(pattern, genre, mood or "neutral")
        elif variation_type == VariationType.TIME_SIGNATURE_SHIFT:
            return self._create_time_signature_variation(pattern, genre, mood or "neutral")
        return None

    def _create_key_transposition(self, pattern: str, genre: str, mood: str) -> Optional[Variation]:
        """Create a key transposition variation."""
        # Parse the pattern to get notes
        notes = pattern.strip('[]').split(',') if pattern.startswith('[') else [pattern]
        notes = [note.strip() for note in notes]
        
        # Determine transposition based on genre and mood
        if genre == "jazz":
            transposition = random.choice([-2, -1, 1, 2])  # More adventurous for jazz
        elif mood == "energetic":
            transposition = random.choice([1, 2])  # Upward transposition for energy
        elif mood == "calm":
            transposition = random.choice([-1, 0])  # Downward or no transposition for calm
        else:
            transposition = random.choice([-1, 0, 1])  # Standard transposition
            
        # Create transposed notes
        transposed_notes = []
        for note in notes:
            # Parse the note
            note_name = note[0].upper()
            octave = int(note[-1])
            # Transpose the note
            new_octave = octave + (transposition // 12)
            new_note = chr((ord(note_name) - ord('A') + transposition) % 12 + ord('A'))
            transposed_notes.append(f"{new_note}{new_octave}")
            
        # Create the variation
        return Variation(
            type=VariationType.KEY_TRANSPOSITION,
            original_pattern=pattern,
            modified_pattern=f"[{','.join(transposed_notes)}]",
            genre=genre,
            mood=mood,
            key="C"  # Default key
        )

    def _create_rhythmic_variation(self, pattern: str, genre: str, mood: str) -> Optional[Variation]:
        """Create a rhythmic variation."""
        # Parse the pattern to get notes
        notes = pattern.strip('[]').split(',') if pattern.startswith('[') else [pattern]
        notes = [note.strip() for note in notes]
        
        # Determine rhythmic variation based on genre and mood
        if genre == "jazz":
            # More syncopated for jazz
            durations = ["eighth", "sixteenth"]
        elif mood == "energetic":
            # Faster rhythms for energetic mood
            durations = ["eighth", "sixteenth"]
        elif mood == "calm":
            # Longer durations for calm mood
            durations = ["half", "quarter"]
        else:
            durations = ["quarter", "eighth"]
            
        # Create rhythmically varied notes
        varied_notes = []
        for note in notes:
            duration = random.choice(durations)
            varied_notes.append(f"{note}:{duration}")
            
        # Create the variation
        return Variation(
            type=VariationType.RHYTHMIC_ALTERATION,
            original_pattern=pattern,
            modified_pattern=f"[{','.join(varied_notes)}]",
            genre=genre,
            mood=mood,
            key="C"  # Default key
        )

    def _create_scale_degree_variation(self, pattern: str, genre: str, mood: str) -> Optional[Variation]:
        """Create a scale degree variation."""
        # Parse the pattern to get notes
        notes = pattern.strip('[]').split(',') if pattern.startswith('[') else [pattern]
        notes = [note.strip() for note in notes]
        
        # Determine scale degree modification based on genre and mood
        if genre == "jazz":
            # More chromatic for jazz
            degrees = [-1, 0, 1, 2]
        elif mood == "energetic":
            # More upward movement for energy
            degrees = [0, 1, 2]
        elif mood == "calm":
            # More diatonic for calm
            degrees = [-1, 0, 1]
        else:
            degrees = [-1, 0, 1]
            
        # Create scale-degree varied notes
        varied_notes = []
        for note in notes:
            # Parse the note
            note_name = note[0].upper()
            octave = int(note[-1])
            # Modify the note by scale degree
            degree = random.choice(degrees)
            new_note = chr((ord(note_name) - ord('A') + degree) % 12 + ord('A'))
            varied_notes.append(f"{new_note}{octave}")
            
        # Create the variation
        return Variation(
            type=VariationType.SCALE_DEGREE_MOD,
            original_pattern=pattern,
            modified_pattern=f"[{','.join(varied_notes)}]",
            genre=genre,
            mood=mood,
            key="C"  # Default key
        )

    def _create_mood_variation(self, pattern: str, genre: str, mood: str) -> Optional[Variation]:
        """Create a mood-based variation."""
        # Parse the pattern to get notes
        notes = pattern.strip('[]').split(',') if pattern.startswith('[') else [pattern]
        notes = [note.strip() for note in notes]
        
        # Determine dynamics based on mood
        if mood == "energetic":
            dynamic = "ff"
        elif mood == "calm":
            dynamic = "p"
        elif mood == "sad":
            dynamic = "mp"
        elif mood == "happy":
            dynamic = "f"
        else:
            dynamic = "mf"
            
        # Create dynamically varied notes
        varied_notes = []
        for note in notes:
            varied_notes.append(f"{note}:{dynamic}")
            
        # Create the variation
        return Variation(
            type=VariationType.MOOD_ADJUSTMENT,
            original_pattern=pattern,
            modified_pattern=f"[{','.join(varied_notes)}]",
            genre=genre,
            mood=mood,
            key="C"  # Default key
        )

    def _create_technique_variation(self, pattern: str, genre: str, mood: str) -> Optional[Variation]:
        """Create a technique-based variation."""
        # Parse the pattern to get notes
        notes = pattern.strip('[]').split(',') if pattern.startswith('[') else [pattern]
        notes = [note.strip() for note in notes]
        
        # Determine technique based on genre and mood
        if genre == "jazz":
            techniques = ["staccato", "legato", "glissando"]
        elif mood == "energetic":
            techniques = ["staccato", "marcato"]
        elif mood == "calm":
            techniques = ["legato", "tenuto"]
        else:
            techniques = ["legato", "staccato"]
            
        # Create technique-varied notes
        varied_notes = []
        for note in notes:
            technique = random.choice(techniques)
            varied_notes.append(f"{note}:{technique}")
            
        # Create the variation
        return Variation(
            type=VariationType.TECHNIQUE_VARIATION,
            original_pattern=pattern,
            modified_pattern=f"[{','.join(varied_notes)}]",
            genre=genre,
            mood=mood,
            key="C",  # Default key
            technique=random.choice(techniques)
        )

    def _create_time_signature_variation(self, pattern: str, genre: str, mood: str) -> Optional[Variation]:
        """Create a time signature variation."""
        # Parse the pattern to get notes
        notes = pattern.strip('[]').split(',') if pattern.startswith('[') else [pattern]
        notes = [note.strip() for note in notes]
        
        # Determine time signature based on genre and mood
        if genre == "jazz":
            time_signatures = ["3/4", "6/8"]
        elif mood == "energetic":
            time_signatures = ["4/4", "6/8"]
        elif mood == "calm":
            time_signatures = ["3/4", "4/4"]
        else:
            time_signatures = ["4/4"]
            
        # Create time signature varied notes
        varied_notes = []
        for note in notes:
            varied_notes.append(note)
            
        # Create the variation
        return Variation(
            type=VariationType.TIME_SIGNATURE_SHIFT,
            original_pattern=pattern,
            modified_pattern=f"[{','.join(varied_notes)}]",
            genre=genre,
            mood=mood,
            key="C",  # Default key
            time_signature=random.choice(time_signatures)
        )

    def get_variations(self, 
                      pattern: str,
                      instrument: str,
                      genre: str,
                      count: int = 1,
                      mood: Optional[str] = None,
                      variation_types: Optional[List[VariationType]] = None) -> List[Variation]:
        """
        Get a specified number of variations for a pattern.
        
        Args:
            pattern: Original pattern to vary
            instrument: Target instrument
            genre: Musical genre
            count: Number of variations to generate
            mood: Optional mood specification
            variation_types: Optional list of specific variation types to use
        
        Returns:
            List of Variation objects
        """
        variations = []
        available_types = variation_types or list(VariationType)
        
        for _ in range(count):
            variation_type = random.choice(available_types)
            variation = self.create_variation(pattern, instrument, genre, variation_type, mood)
            if variation:
                variations.append(variation)
        
        return variations

    def validate_variation(self, variation: Variation, instrument: str) -> bool:
        """
        Validate if a variation is suitable for the given instrument.
        
        Args:
            variation: Variation to validate
            instrument: Target instrument
        
        Returns:
            Boolean indicating if variation is valid
        """
        # Implementation for validation
        # Check range, playability, and genre-specific rules
        pass

    def save_variation(self, variation: Variation) -> None:
        """
        Save a variation to the variations dictionary.
        
        Args:
            variation: Variation to save
        """
        key = f"{variation.genre}_{variation.mood}_{variation.type.name}"
        if key not in self.variations:
            self.variations[key] = []
        self.variations[key].append(variation)

    def get_cached_variations(self, 
                            genre: str,
                            mood: Optional[str] = None,
                            variation_type: Optional[VariationType] = None) -> List[Variation]:
        """
        Retrieve cached variations matching the specified criteria.
        
        Args:
            genre: Musical genre
            mood: Optional mood specification
            variation_type: Optional variation type
        
        Returns:
            List of matching Variation objects
        """
        results = []
        for key, variations in self.variations.items():
            if all([
                genre in key,
                (not mood or mood in key),
                (not variation_type or variation_type.name in key)
            ]):
                results.extend(variations)
        return results
