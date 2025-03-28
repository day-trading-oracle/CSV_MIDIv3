"""
Test script for bass functionality.
"""

from midi_generator import generate_midi

def create_test_song():
    """Create a test song with a C major scale and bass enabled"""
    # C major scale (C4 to C5)
    c_major_scale = [60, 62, 64, 65, 67, 69, 71, 72]  # MIDI note numbers
    
    # Create song data structure
    song_data = {
        'title': 'Test Scale with Bass',
        'tempo': 120,
        'time_signature': '4/4',
        'instrument': 0,  # Piano
        'enable_bass': True,  # Enable bass track
        'bass_style': 'walking',  # Use walking bass pattern
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

def main():
    print("Creating test MIDI file with bass...")
    
    # Create test song data
    song_data = create_test_song()
    
    # Test different bass styles
    styles = ['walking', 'rock', 'funk', 'jazz', 'pop']
    
    for style in styles:
        print(f"\nGenerating MIDI with {style} bass style...")
        song_data['bass_style'] = style
        
        output_file = generate_midi(
            song_data,
            accompaniment_style='basic',
            genre='classical'
        )
        
        if output_file:
            print(f"Successfully generated: {output_file}")
        else:
            print("Failed to generate MIDI file")
    
    print("\nAll test files generated successfully!")

if __name__ == "__main__":
    main() 