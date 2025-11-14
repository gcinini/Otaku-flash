"""
Atari 2600 ROM Builder

This module processes Atari 2600 ROM files and generates C source code for the
Raspberry Pi Pico to emulate the cartridge hardware. It uses the Stella emulator
to detect the cartridge type and delegates to type-specific builders.

Supported cartridge types:
    - 2K: Simple 2KB ROM
    - 4K: Simple 4KB ROM
    - F4, F4SC: 32KB with bankswitching
    - F6, F6SC: 16KB with bankswitching
    - F8, F8SC: 8KB with bankswitching
    - FE: FE bankswitching (not fully supported on Pico)

Usage:
    python build26.py <rom_file.bin>

Author: Karri Kaksonen, 2024
Based on work by Nick Bild, 2021
"""

import sys
import subprocess
import build26rom2k
import build26rom4k
import build26romF4
import build26romF4SC
import build26romF6
import build26romF6SC
import build26romF8
import build26romF8SC
import build26romFE

class rom:
    """
    Atari 2600 ROM processor class.
    
    This class handles the detection and processing of Atari 2600 cartridge ROMs,
    using the Stella emulator to identify the cartridge type and generating
    appropriate C code for hardware emulation on the Raspberry Pi Pico.
    
    Attributes:
        fname (str): Path to the ROM file to process
        type (bytes): Detected cartridge type (e.g., b'2K*', b'F8*', etc.)
    """
    
    def __init__(self, fname):
        """
        Initialize the ROM processor.
        
        Args:
            fname (str): Path to the Atari 2600 ROM file
        """
        self.fname = fname

    def carttype(self):
        """
        Detect the cartridge type using the Stella emulator.
        
        Executes the Stella emulator with the -rominfo flag to analyze the ROM
        and determine its bankswitch type. The detected type is stored in self.type.
        
        Requires:
            Stella emulator must be installed and available in PATH
        """
        output = subprocess.check_output(['stella', '-rominfo', self.fname])
        for i in output.splitlines():
            l = i.strip()
            if l.startswith(bytes('Bankswitch Type:', 'utf-8')):
                b = l[16:].strip().split()
                self.type = b[0]

    def createrom(self):
        """
        Generate C source code for the detected cartridge type.
        
        This method first detects the cartridge type, then creates an instance
        of the appropriate ROM builder class and generates a 'rom.c' file
        containing the embedded ROM data and emulation logic for the Raspberry
        Pi Pico.
        
        Outputs:
            rom.c: C source file with ROM data and emulation code
        
        Prints:
            Warnings for unsupported or problematic cartridge types
        """
        self.carttype()
        if self.type == b'2K*':
            r = build26rom2k.rom(self.fname)
            fname = 'rom.c'
            f = open(fname, 'w')
            r.writedata(f)
            f.close()
        elif self.type == b'4K*':
            r = build26rom4k.rom(self.fname)
            fname = 'rom.c'
            f = open(fname, 'w')
            r.writedata(f)
            f.close()
        elif self.type == b'F4*':
            r = build26romF4.rom(self.fname)
            fname = 'rom.c'
            f = open(fname, 'w')
            r.writedata(f)
            f.close()
        elif self.type == b'F4SC*':
            r = build26romF4SC.rom(self.fname)
            fname = 'rom.c'
            f = open(fname, 'w')
            r.writedata(f)
            f.close()
        elif self.type == b'F6*':
            r = build26romF6.rom(self.fname)
            fname = 'rom.c'
            f = open(fname, 'w')
            r.writedata(f)
            f.close()
        elif self.type == b'F6SC*':
            r = build26romF6SC.rom(self.fname)
            fname = 'rom.c'
            f = open(fname, 'w')
            r.writedata(f)
            f.close()
        elif self.type == b'F8*':
            r = build26romF8.rom(self.fname)
            fname = 'rom.c'
            f = open(fname, 'w')
            r.writedata(f)
            f.close()
        elif self.type == b'F8SC*':
            r = build26romF8SC.rom(self.fname)
            fname = 'rom.c'
            f = open(fname, 'w')
            r.writedata(f)
            f.close()
        elif self.type == b'FE*':
            r = build26romFE.rom(self.fname)
            fname = 'rom.c'
            f = open(fname, 'w')
            r.writedata(f)
            f.close()
            print(self.type, 'the Pico is too slow. Not supported, yet')
        else:
            print(self.type, 'not supported, yet')

if __name__ == '__main__':
    """
    Main execution block.
    
    Processes command-line arguments and initiates ROM conversion.
    
    Command-line Arguments:
        rom_file: Path to the Atari 2600 ROM file to process
        
    Example:
        python build26.py game.bin
    """
    fname=str(sys.argv[len(sys.argv)-1])
    game = rom(fname)
    game.createrom()
