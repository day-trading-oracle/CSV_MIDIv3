"""
Utility functions for MIDI music generation.
"""

def normalize_velocity(velocity: int, min_vel: int = 30, max_vel: int = 120) -> int:
    """
    Normalize a velocity value to be within the specified range.
    
    Args:
        velocity: The input velocity value
        min_vel: The minimum allowed velocity (default: 30)
        max_vel: The maximum allowed velocity (default: 120)
        
    Returns:
        The normalized velocity value
    """
    return max(min_vel, min(max_vel, velocity)) 