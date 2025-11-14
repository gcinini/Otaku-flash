"""
Atari 7800 ROM Information Display

This module parses and displays detailed information from Atari 7800 ROM files
in the A78 format. It extracts metadata from the 128-byte header including
cartridge name, size, type flags, controller information, video format, and
special features.

This is a diagnostic tool for inspecting ROM file contents without generating
code for the Pico hardware.

Usage:
    python info78.py <rom_file.a78>

Output:
    Displays cartridge information including:
    - Version
    - Name
    - Size
    - Cartridge type and features
    - Controller types
    - Video format (NTSC/PAL)
    - Save features
    - IRQ configuration
    - Slot devices

Author: Karri Kaksonen, 2024
Based on work by Nick Bild, 2021
"""

import sys
import subprocess
import build78rom8k
import build78rom16k
import build78rom32k
import build78rom48k
import build78romAB
import build78romSG
import build78romSGEF
import build78romSGER

class rom:
    """
    Atari 7800 ROM information parser and display class.
    
    This class parses the A78 header format and displays detailed information
    about the cartridge without generating hardware emulation code.
    
    Attributes:
        fname (str): Path to the ROM file to analyze
        header (bytes): 128-byte A78 header
        version (int): Header format version
        name (str): Cartridge name from header
        size (int): ROM size in bytes
        type (bytes): Detected cartridge type
        CartType (list): List of detected cartridge features
        typeA, typeB (int): Type flag bytes from header
        controller1, controller2: Controller types
        video (str): Video format (NTSC/PAL)
        blending (str): Composite blending setting
        saves: Save feature flags
        irqs: IRQ configuration
        slotdevice: Slot device configuration
    """
    
    def __init__(self, fname):
        """
        Initialize the ROM information parser.
        
        Args:
            fname (str): Path to the Atari 7800 ROM file (.a78 format)
        """
        self.fname = fname

    def carttype(self):
        """
        Parse and display A78 header information.
        
        This method reads and interprets the 128-byte A78 header, extracting
        and printing all relevant cartridge metadata. It analyzes type flags
        to identify features and determines cartridge support status.
        
        The A78 header structure includes:
            - Byte 0: Version
            - Bytes 17-48: Cartridge name (UTF-8)
            - Bytes 49-52: ROM size (big-endian)
            - Byte 53-54: Type flags (typeA, typeB bitflags)
            - Byte 55-56: Controller types
            - Byte 57: Video format and blending
            - Byte 58: Save features
            - Byte 63: IRQ configuration
            - Byte 64: Slot device
            
        Prints:
            All extracted cartridge information and features
        """
        self.type = b'Not supported'
        with open(self.fname, 'rb') as f:
            data = f.read()
        self.header = data[:128]
        self.version = self.header[0]
        print('Version:', self.version)
        self.name = str(self.header[17:49], 'utf-8')
        print('Name:', self.name)
        self.size = int.from_bytes(self.header[49:53], 'big')
        print('Size:', self.size)
        if self.size == 8192:
            self.type = b'8K'
        elif self.size == 16384:
            self.type = b'16K'
        elif self.size == 32768:
            self.type = b'32K'
        elif self.size == 49152:
            self.type = b'48K'
        self.CartType = []
        self.typeA = self.header[53]
        self.typeB = self.header[54]
        if self.typeB & 2:
            self.CartType.append('SUPER')
            self.type = b'SG'
        if self.typeB & 16:
            self.CartType.append('EXFIX')
            if self.type == b'SG':
                self.type = b'SGEF'
            else:
                self.type = b'Not supported'
        if self.typeB & 4:
            self.CartType.append('EXRAM')
            if self.type == b'SG':
                self.type = b'SGER'
            else:
                self.type = b'Not supported'
        if self.typeA & 32:
            self.CartType.append('BANKSET')
            self.type = b'Not supported'
        if self.typeA & 16:
            self.CartType.append('SOUPER')
            self.type = b'Not supported'
        if self.typeA & 2:
            self.CartType.append('ABSOLUTE')
            self.type = b'AB'
            print(self.type)
        if self.typeA & 64:
            self.CartType.append('EXRAM/M2')
            self.type = b'Not supported'
        if self.typeB & 8:
            self.CartType.append('EXROM')
            self.type = b'Not supported'
        if self.typeA & 128:
            self.CartType.append('POKEY @0800')
            self.type = b'Not supported'
        if self.typeA & 8:
            self.CartType.append('YM2151 @0461')
            self.type = b'Not supported'
        if self.typeA & 4:
            self.CartType.append('POKEY @0440')
            self.type = b'Not supported'
        if self.typeA & 1:
            self.CartType.append('ACTIVISION')
            self.type = b'Not supported'
        if self.typeB & 128:
            self.CartType.append('EXRAM/A8')
            self.type = b'Not supported'
        if self.typeB & 64:
            self.CartType.append('POKEY @0450')
            self.type = b'Not supported'
        if self.typeB & 32:
            self.CartType.append('EXRAM/X2')
            self.type = b'Not supported'
        if self.typeB & 1:
            self.CartType.append('POKEYU@4000')
            self.type = b'Not supported'
        print('Cartridge type:', self.CartType)
        self.controller1 = self.header[55]
        if self.controller1 == 1:
            self.controller1 = 'ProLine'
        print('Controller 1:', self.controller1)
        self.controller2 = self.header[56]
        if self.controller2 == 1:
            self.controller2 = 'ProLine'
        print('Controller 2:', self.controller2)
        self.video = self.header[57]
        if self.video & 2 != 0:
            self.blending = 'Composite blending'
            print(self.blending)
        if self.video & 1 == 0:
            self.video = 'NTSC'
        else:
            self.video = 'PAL'
        print(self.video)
        self.saves = self.header[58]
        if self.saves & 1 != 0:
            print('High Score cartridge')
        if self.saves & 2 != 0:
            print('SaveKey or AtariVox')
        self.irqs = self.header[63]
        if self.irqs != 0:
            print('IRQ', self.irqs)
            self.type = b'Not supported'
        self.slotdevice = self.header[64]
        if self.slotdevice != 0:
            print('Slot device:', self.slotdevice)
            if self.type == b'AB':
                pass
            elif self.type == b'SGEF':
                pass
            else:
                self.type = b'Not supported'
        print(self.CartType)

if __name__ == '__main__':
    """
    Main execution block.
    
    Processes command-line arguments and displays ROM information.
    
    Command-line Arguments:
        rom_file: Path to the Atari 7800 ROM file (.a78) to analyze
        
    Example:
        python info78.py game.a78
    """
    fname=str(sys.argv[len(sys.argv)-1])
    game = rom(fname)
    game.carttype()
