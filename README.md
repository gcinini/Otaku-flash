# Otaku-flash
A single game flash card for Atari 2600, Atari 7800 and Atari 2600+

The logic in this card is based on Raspberrypi Pico
![](https://github.com/karrika/Otaku-flash/blob/main/doc/Pico2600f.png)

The startup of the Pico is too slow for a real Atari 7800. The way I
run the game is by:
- inserting the card when the power is off
- then I connect a powerbank to Pico's USB socket
- finally I power on the console
This allows the Pico to prepare everything before I power on
my Atari 7800 console. The schottky diode in the cart prevents the
powerbank to power on the console when the cart has power but the
console has not.

The new Atari 2600+ does not have a startup problem. But the Otaku cart
may draw too much current so I am also using the powerbank when the cart
is in the 2600+.

The cart has a 2600 connector and a 7800 connector. The 7800 connector can
be used for running all games. The 2600 connector only works for 2600 games.

Programming the cart:
- keep the button pressed while inserting the USB cable to the PC
- release the button
- drag a a game.uf2 file to the folder opened by the Otaku card

For converting a game into the uf2 format you need to install Raspberry Pico
tools with the SDK kit.



Fork by gcinini - https://github.com/gcinini


👉 New here? Check out the [Getting Started Guide](GettingStarted.md) for installation and usage instructions.
 ----------------

 # 🕹️ Atari 2600 ROM to UF2 Converter

This project provides Python build scripts to convert **Atari 2600 ROM files** into `.uf2` format for use with a **Raspberry Pi Pico**.  
The Pico then acts as a physical cartridge, allowing you to run ROMs directly on real Atari 2600/7800 hardware.

---

## ⚙️ Purpose of the Build Scripts
- **Input:** Standard Atari 2600 ROM files (2K, 4K, F4, F6, F8, FE bankswitching formats)  
- **Output:** A `.uf2` file that the Raspberry Pi Pico can load  
- **Goal:** Make the Pico behave like a physical cartridge, so the console sees the ROM as if it were a real chip  

---

## 📂 Key Scripts

### 1. `build26rom2k.py`
- Handles **2 KB ROMs** (the simplest Atari 2600 format)  
- Reads the binary ROM file  
- Pads or arranges it into the correct memory layout for the Pico  
- Writes out a `.uf2` file containing the ROM data plus metadata for the Pico bootloader  

---

### 2. `build26rom4k.py`
- Similar to the 2K script but for **4 KB ROMs**  
- Ensures the ROM is aligned correctly in memory  
- Adds headers so the Pico knows how to map the ROM into its flash  

---

### 3. `build26romF4.py`, `build26romF6.py`, `build26romF8.py`, `build26romFE.py`
- Handle **bankswitched ROMs** (larger than 4 KB)  
- Bankswitching means the ROM is divided into chunks (banks), and the Atari 2600 switches between them during gameplay  

These scripts:
- Split the ROM into banks  
- Insert the correct switching logic into the `.uf2` file  
- Ensure the Pico emulates the bankswitching behavior of real cartridges  

---

## 🧩 How They Work (Step by Step)

1. **Open ROM file** → `open(filename, "rb")`  
2. **Read binary data** → `rom = f.read()`  
3. **Check size** → Ensure it matches expected (2K, 4K, etc.)  
4. **Pad or split** → Add padding or divide into banks if needed  
5. **Wrap in UF2 format** → UF2 is a block-based firmware format for the Pico  
6. **Write output** → Save as `game.uf2`, ready to drag-and-drop onto the Pico  

---

## 🚀 Usage
1. Place your Atari 2600 ROM file in the project directory.  
2. Run the appropriate build script for your ROM size or bankswitching type.  
3. Copy the generated `.uf2` file to your Raspberry Pi Pico.  
4. Insert the Pico cartridge into your Atari console and enjoy!  

## ❗ Troubleshooting
If your Pico doesn’t appear as a USB drive, hold the BOOTSEL button while plugging it in.

If the ROM size doesn’t match, check that you’re using the correct script (2K vs 4K vs bankswitched).

For console compatibility issues, verify your board wiring matches the KiCad design.
