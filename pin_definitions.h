/*
 * Otaku-flash Pin Definitions
 * 
 * GPIO pin mappings for Raspberry Pi Pico to Atari cartridge bus.
 * These definitions map the Pico's GPIO pins to the Atari 2600/7800
 * cartridge connector signals.
 * 
 * CRITICAL: Do not change these pin assignments!
 * The code contains performance optimizations that depend on these
 * specific pin positions for fast address decoding and data output.
 * 
 * Pin Groups:
 *   - Address pins (A0-A15): GPIO 0-14, 26
 *   - Control pins (RW, HALT): GPIO 25, 27
 *   - Data pins (D0-D7): GPIO 15-22
 * 
 * Author: Karri Kaksonen, 2024
 * Based on work by Nick Bild, 2021
 */

// Don't change the pin definitions.
// Optimizations expect that they are in these positions.

// Address pins.
// These 16 pins read the address bus from the Atari console.
// A0-A14 are sequential for fast masking operations.
#define A0 0
#define A1 1
#define A2 2
#define A3 3
#define A4 4
#define A5 5
#define A6 6
#define A7 7
#define A8 8
#define A9 9
#define A10 10
#define A11 11
#define A12 12
#define A13 13
#define A14 14
#define A15 26

// Control pins.
// RW: Read/Write signal from console
// HALT: Halt signal for synchronization
#define RW 25
#define HALT 27

// Data pins.
// These 8 pins output data to the Atari console data bus.
// Sequential arrangement enables fast 8-bit data output.
#define D0 15
#define D1 16
#define D2 17
#define D3 18
#define D4 19
#define D5 20
#define D6 21
#define D7 22
