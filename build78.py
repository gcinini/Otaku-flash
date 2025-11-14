"""
Atari 7800 ROM Builder

This module processes Atari 7800 ROM files and generates C source code for the
Raspberry Pi Pico to emulate the cartridge hardware. It parses the A78 header
format to detect cartridge features and delegates to type-specific builders.

Supported cartridge types:
    - 8K, 16K, 32K, 48K: Standard ROM sizes
    - AB: Absolute addressing
    - SG: SuperGame bankswitching
    - SGEF: SuperGame with EXFIX
    - SGER: SuperGame with EXRAM
    - SGERP450: SuperGame with EXRAM and POKEY @0450
    - SGERYMP450: SuperGame with EXRAM, YM2151 and POKEY @0450

The A78 header format specifies cartridge size, type flags, controllers,
video format, save features, and other hardware characteristics.

Usage:
    python build78.py <rom_file.a78>

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
import build78romSGERP450
import build78romSGERYMP450

class rom:
    """
    Atari 7800 ROM processor class.
    
    This class handles the detection and processing of Atari 7800 cartridge ROMs,
    parsing the A78 header format to identify cartridge features and generating
    appropriate C code for hardware emulation on the Raspberry Pi Pico.
    
    Attributes:
        fname (str): Path to the ROM file to process
        header (bytes): 128-byte A78 header
        version (int): Header format version
        name (str): Cartridge name from header
        size (int): ROM size in bytes
        type (bytes): Detected cartridge type
        CartType (list): List of detected cartridge features
        typeA, typeB (int): Type flag bytes from header
        controller1, controller2: Controller types
        video (str): Video format (NTSC/PAL)
        saves: Save feature flags
        irqs: IRQ configuration
        slotdevice: Slot device configuration
    """
    
    def __init__(self, fname):
        """
        Initialize the ROM processor.
        
        Args:
            fname (str): Path to the Atari 7800 ROM file (.a78 format)
        """
        self.fname = fname

    def carttype(self):
        """
        Parse the A78 header and detect cartridge type and features.
        
        The A78 header is a 128-byte structure containing:
            - Byte 0: Version
            - Bytes 17-48: Cartridge name (UTF-8)
            - Bytes 49-52: ROM size (big-endian)
            - Byte 53-54: Type flags (typeA, typeB)
            - Byte 55-56: Controller types
            - Byte 57: Video format
            - Byte 58: Save features
            - Byte 63: IRQ configuration
            - Byte 64: Slot device
            
        Type flags are bitmasks indicating features like bankswitching,
        SuperGame, EXRAM, POKEY sound chips, and other hardware.
        
        Sets:
            self.type: Detected cartridge type (e.g., b'8K', b'SG', b'SGER')
            self.CartType: List of feature strings
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
            if self.type == b'SGER':
                self.type = b'SGERYM'
            else:
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
            if self.type == b'SGER':
                self.type = b'SGERP450'
            elif self.type == b'SGERYM':
                self.type = b'SGERYMP450'
            else:
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
            elif self.type == b'SGER':
                pass
            elif self.type == b'SGERP450':
                pass
            elif self.type == b'SGERYMP450':
                pass
            else:
                self.type = b'Not supported'

    def createrom(self):
        """
        Generate C source code for the detected cartridge type.
        
        This method first detects the cartridge type by parsing the A78 header,
        then creates an instance of the appropriate ROM builder class and
        generates a 'rom.c' file containing the embedded ROM data and emulation
        logic for the Raspberry Pi Pico.
        
        Outputs:
            rom.c: C source file with ROM data and emulation code
        
        Prints:
            Warnings for unsupported cartridge types
        """
        self.carttype()
        if self.type == b'8K':
            r = build78rom8k.rom(self.fname)
            fname = 'rom.c'
            f = open(fname, 'w')
            r.writedata(f)
            f.close()
        elif self.type == b'16K':
            r = build78rom16k.rom(self.fname)
            fname = 'rom.c'
            f = open(fname, 'w')
            r.writedata(f)
            f.close()
        elif self.type == b'32K':
            r = build78rom32k.rom(self.fname)
            fname = 'rom.c'
            f = open(fname, 'w')
            r.writedata(f)
            f.close()
        elif self.type == b'48K':
            r = build78rom48k.rom(self.fname)
            fname = 'rom.c'
            f = open(fname, 'w')
            r.writedata(f)
            f.close()
        elif self.type == b'AB':
            r = build78romAB.rom(self.fname)
            fname = 'rom.c'
            f = open(fname, 'w')
            r.writedata(f)
            f.close()
        elif self.type == b'SG':
            r = build78romSG.rom(self.fname)
            fname = 'rom.c'
            f = open(fname, 'w')
            r.writedata(f)
            f.close()
        elif self.type == b'SGEF':
            r = build78romSGEF.rom(self.fname)
            fname = 'rom.c'
            f = open(fname, 'w')
            r.writedata(f)
            f.close()
        elif self.type == b'SGER':
            r = build78romSGER.rom(self.fname)
            fname = 'rom.c'
            f = open(fname, 'w')
            r.writedata(f)
            f.close()
        elif self.type == b'SGERP450':
            r = build78romSGERP450.rom(self.fname)
            fname = 'rom.c'
            f = open(fname, 'w')
            r.writedata(f)
            f.close()
        elif self.type == b'SGERYMP450':
            r = build78romSGERYMP450.rom(self.fname)
            fname = 'rom.c'
            f = open(fname, 'w')
            r.writedata(f)
            f.close()
        else:
            print(self.type, 'not supported, yet')

if __name__ == '__main__':
    """
    Main execution block.
    
    Processes command-line arguments and initiates ROM conversion.
    
    Command-line Arguments:
        rom_file: Path to the Atari 7800 ROM file (.a78) to process
        
    Example:
        python build78.py game.a78
    """
    fname=str(sys.argv[len(sys.argv)-1])
    print(fname)
    game = rom(fname)
    game.createrom()
