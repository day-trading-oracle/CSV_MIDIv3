"""
Instrument Manager module for managing different instruments
"""

from typing import Dict, Optional, Type

from .base import BaseInstrument
from .piano import Piano
from .bass import Bass
from .drums import Drums
from .guitar import Guitar

class InstrumentManager:
    """Manages the creation and configuration of different instruments."""
    
    def __init__(self):
        """Initialize the instrument manager."""
        self.instruments: Dict[str, Type[BaseInstrument]] = {
            'piano': Piano,
            'bass': Bass,
            'drums': Drums,
            'guitar': Guitar,
        }
    
    def get_instrument(
        self,
        instrument_type: str,
        program: Optional[int] = None,
        **kwargs
    ) -> BaseInstrument:
        """
        Get an instance of the specified instrument type.
        
        Args:
            instrument_type: Type of instrument to create
            program: Optional MIDI program number override
            **kwargs: Additional arguments to pass to the instrument constructor
            
        Returns:
            An instance of the requested instrument
            
        Raises:
            ValueError: If the instrument type is not recognized
        """
        if instrument_type not in self.instruments:
            raise ValueError(f"Unknown instrument type: {instrument_type}")
        
        instrument_class = self.instruments[instrument_type]
        if program is not None:
            kwargs['program'] = program
        
        return instrument_class(**kwargs)
    
    def list_instruments(self) -> list[str]:
        """
        Get a list of available instrument types.
        
        Returns:
            List of instrument type names
        """
        return list(self.instruments.keys())
    
    def register_instrument(self, name: str, instrument_class: Type[BaseInstrument]):
        """
        Register a new instrument type.
        
        Args:
            name: Name to register the instrument under
            instrument_class: The instrument class to register
        """
        self.instruments[name] = instrument_class 