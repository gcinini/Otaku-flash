"""
Atari 2600 F8 Bankswitching ROM Builder

This module generates C source code to emulate an 8K Atari 2600 ROM cartridge
with F8 bankswitching on a Raspberry Pi Pico. F8 bankswitching divides the 8K
ROM into two 4K banks that can be switched by accessing specific addresses.

F8 Bankswitching Details:
    - Total ROM: 8KB (2 x 4KB banks)
    - Address 0x1FF8: Switch to bank 0
    - Address 0x1FF9: Switch to bank 1
    - Visible window: 4KB at a time

The generated code monitors address lines, performs bankswitching when
triggered, and outputs data from the active bank.

Author: Karri Kaksonen, 2024
Based on work by Nick Bild, 2021
"""

import sys

class rom:
    """
    F8 bankswitching ROM builder class for Atari 2600 cartridges.
    
    This class reads an 8KB ROM file and generates C source code that embeds
    the ROM data and implements F8 bankswitching emulation logic for the
    Raspberry Pi Pico.
    
    Attributes:
        data (bytes): The raw 8KB ROM data read from the input file
    """
    
    def __init__(self, fname):
        """
        Initialize the ROM builder and load ROM data.
        
        Args:
            fname (str): Path to the 8KB ROM file with F8 bankswitching
        """
        with open(fname, 'rb') as f:
            self.data = f.read()

    def writedata(self, f):
        """
        Generate and write the C source code for F8 bankswitching ROM emulation.
        
        This method creates a complete C source file containing:
            1. ROM data array with all 8KB of cartridge contents
            2. GPIO initialization for address and data buses
            3. Main loop that monitors address lines
            4. Bankswitching logic triggered by specific address accesses
            5. Data bus control based on ROM access detection
        
        The generated code runs at 291 MHz (overclocked) for sufficient speed
        to handle bankswitching and data output in real-time.
        
        Bankswitching Logic:
            - Access to 0x1FF8 switches to bank 0 (offset 0)
            - Access to 0x1FF9 switches to bank 1 (offset 4096)
            - Each bank is 4KB, addressable through 0x0-0xFFF
        
        Args:
            f (file object): Open file handle to write the C code to
        """
        code = '''
/*
* Otaku-flash
* Simulate a 8k Atari 2600 ROM chip with F8 bankswitching on a
* Raspberry Pi Pico.
* Karri Kaksonen, 2024
* based on work by
* Nick Bild 2021
*/

#include "pico/stdlib.h"
#include "hardware/clocks.h"
#include "hardware/vreg.h"
#include <stdlib.h>

#define ROM_SIZE 0x1000

uint8_t rom_contents[2*ROM_SIZE] __attribute__ ((aligned(2*ROM_SIZE))) = {
'''
        f.write(code)
        for i in range(0, len(self.data), 8):
            f.write('    ')
            for j in range(7):
                f.write("0x{:02x}".format(self.data[i + j]) + ', ')
            if i + 7 < len(self.data) - 1:
                f.write("0x{:02x}".format(self.data[i + 7]) + ',\n')
            else:
                f.write("0x{:02x}".format(self.data[i + 7]))
        code = '''
};

int main() {
    uint32_t rawaddr;
    uint16_t addr;
    uint16_t bank;
    uint8_t rom_in_use;

    rom_in_use = 1;
    bank = 0;

    // Set system clock speed.
    // 291 MHz
    vreg_set_voltage(VREG_VOLTAGE_1_20);
    set_sys_clock_pll(1164000000, 4, 1);
    
    // GPIO setup.
    gpio_init_mask(0xe7fffff);         // All pins.
    gpio_set_dir_in_masked(0xe007fff); // Address pins.
    gpio_set_dir_out_masked(0x7f8000); // Data pins.
    
    // Continually check address lines and
    // put associated data on bus.
    while (true) {
        // Get address
        rawaddr = gpio_get_all();
        addr = rawaddr & 0x0fff;
        // Check for rom access
        if (rawaddr & 0x1000) {
            // Put data on the bus
            gpio_put_masked(0x7f8000, rom_contents[addr + bank] << 15);
            if (!rom_in_use) {
                gpio_set_dir_out_masked(0x7f8000);
                rom_in_use = 1;
            }
            // Do bankswitching
            switch (rawaddr & 0x1fff) {
            case 0x1ff8:
                bank = 0;
                break;
            case 0x1ff9:
                bank = 4096;
                break;
            default:
                break;
            }
        } else {
            if (rom_in_use) {
                gpio_set_dir_in_masked(0x7f8000);
                rom_in_use = 0;
            }
        }
    }
}
'''
        f.write(code)

if __name__ == '__main__':
    """
    Main execution block for standalone usage.
    
    Command-line Arguments:
        rom_file: Path to the 8KB F8 bankswitching ROM file to convert
        
    Example:
        python build26romF8.py game.bin
    """
    fname=str(sys.argv[len(sys.argv)-1])
    r = rom(fname)
    fname = 'rom.c'
    f = open(fname, 'w')
    r.writedata(f)
    f.close()

