"""
Atari 2600 4K ROM Builder

This module generates C source code to emulate a 4K Atari 2600 ROM cartridge
on a Raspberry Pi Pico. It creates an inline ROM data array and the main loop
that monitors address lines and outputs corresponding data on the GPIO bus.

The 4K ROM is the most common Atari 2600 cartridge size, used by many
classic games like Pac-Man, Space Invaders, and Pitfall.

Memory Map:
    - ROM_SIZE: 0x1000 (4KB)
    - ROM_MASK: 0x0FFF (address mask)
    - ROM_IN_USE: 0x1000 (flag bit for ROM access detection)

Author: Karri Kaksonen, 2024
Based on work by Nick Bild, 2021
"""

import sys

class rom:
    """
    4K ROM builder class for Atari 2600 cartridges.
    
    This class reads a 4KB ROM file and generates C source code that embeds
    the ROM data and implements the cartridge emulation logic for the
    Raspberry Pi Pico.
    
    Attributes:
        data (bytes): The raw 4KB ROM data read from the input file
    """
    
    def __init__(self, fname):
        with open(fname, 'rb') as f:
            self.data = f.read()

    def writedata(self, f):
        code = '''
/*
* Otaku-flash
* Simulate a 4k Atari 2600 ROM chip with a Raspberry Pi Pico.
* Karri Kaksonen, 2024
* based on work by
* Nick Bild 2021
*/

#include "pico/stdlib.h"
#include "hardware/clocks.h"
#include "hardware/vreg.h"
#include <stdlib.h>

#define ROM_SIZE 0x1000
#define ROM_MASK 0x0fff
#define ROM_IN_USE 0x1000

uint8_t rom_contents[ROM_SIZE] __attribute__ ((aligned(ROM_SIZE))) = {
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

uint32_t addr;
uint8_t rom_in_use;
uint8_t new_rom_in_use;

int main() {
    rom_in_use = 1;

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
        addr = gpio_get_all();
        // Put data corresponding to address
        gpio_put_masked(0x7f8000, rom_contents[addr & ROM_MASK] << 15);
        // Disable data bus output if it was a ROM access
	new_rom_in_use = (addr & ROM_IN_USE) ? 1 : 0;
        if (new_rom_in_use != rom_in_use) {
            rom_in_use = 1 - rom_in_use;
            if (rom_in_use) {
                gpio_set_dir_out_masked(0x7f8000);
            } else {
                gpio_set_dir_in_masked(0x7f8000);
            }
        }
    }
}
'''
        f.write(code)

if __name__ == '__main__':
    fname=str(sys.argv[len(sys.argv)-1])
    r = rom(fname)
    fname = 'rom.c'
    f = open(fname, 'w')
    r.writedata(f)
    f.close()

