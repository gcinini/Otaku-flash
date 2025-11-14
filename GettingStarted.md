# 🚀 Getting Started with Atari 2600 ROM to UF2 Converter

This guide will help you set up your environment and run the build scripts to convert Atari 2600 ROMs into `.uf2` files for the Raspberry Pi Pico.

---

## 🛠️ Prerequisites
- **Python 3.8+** installed on your system  
- A **Raspberry Pi Pico** microcontroller on a board that interfaces it to the Atari  
  - Build one using the KiCad files in the [Otaku folder](Otaku/) in this repo  
  - Or check the shared design on [PCBWay](https://www.pcbway.com/project/shareproject/Otaku_Flash_Cart_for_Ataru_2600_7800_2600_17c45951.html)  
- Atari 2600 ROM files (2K, 4K, or bankswitched formats: F4, F6, F8, FE)  
- USB cable to connect the Pico to your computer  
- Optional: 3D-printed cartridge casing (STL files included in repo)  

## ❗ Troubleshooting
- If your Pico doesn’t appear as a USB drive, hold the BOOTSEL button while plugging it in.
- If the ROM size doesn’t match, check that you’re using the correct script (2K vs 4K vs bankswitched).
- For console compatibility issues, verify your board wiring matches the KiCad design.

---
## 🛠️ Developer Setup (Optional)

If you want to modify the Pico firmware itself (beyond just converting ROMs), you will need:

- Raspberry Pi Pico SDK (C/C++ toolchain)
- CMake and ARM GCC toolchain
- An IDE such as Visual Studio Code with CMake support

Follow the official [Raspberry Pi Pico SDK documentation](https://datasheets.raspberrypi.com/pico/getting-started-with-pico.pdf) to set up your environment.