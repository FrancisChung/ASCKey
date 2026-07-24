# ASCKey

Repurposing an obsolete Stackoverflow Keyboard.

### Introduction

I have a Stackoverflow keyboard that is no longer relevant in 2026.
What way to repurpose this keyboard that reflects the AI Age we live in.

By Flipping the V key vertically, you get an "ASC" keyboard with ASC standing for Anthropic, Stackoverflow and Codex

<img width="2160" height="2880" alt="image" src="https://github.com/user-attachments/assets/9dfbc3af-e80d-4f9d-80a3-a5b02f449f00" />

Pressing each key should open a tab on their respective URLs



### References

Official Docs:


[https://helpdesk.drop.com/hc/en-us/articles/45960109334673-How-to-Configure-Stack-Overflow-The-Key-and-The-Key-V2-Macropad](https://helpdesk.drop.com/hc/en-us/articles/45960109334673-How-to-Configure-Stack-Overflow-The-Key-and-The-Key-V2-Macropad)

Unofficial Guide:


[https://www.helgejohnsen.no/skriverier/how-to-setup-stack-overflow-keyboard](https://www.helgejohnsen.no/skriverier/how-to-setup-stack-overflow-keyboard)


### Resources

TheKey.json file & the .hex file are located in Config:
* Config/3key.hex
* Config/TheKey.json

The following sites needs to be referenced for flashing the keyboard:

https://kbfirmware.com/

https://qmk.fm/toolbox

https://github.com/qmk/qmk_toolbox/pull/499

### Installing the firmware

1. Go to the [archived Keyboard Firmware Builder](https://web.archive.org/web/20260214211516/https://docs.drop.com/thekey.json) linked from Drop's official guide (or kbfirmware.com directly, if still reachable).
2. Upload `Config/TheKey.json` via "Upload Keyboard Firmware Builder configuration".
3. Go to the **Compile** tab and click **Download .hex**.
4. Flash the downloaded `.hex` file to the macropad — see "Flashing on Linux" below for the `dfu-programmer` steps; on Mac/Windows use QMK Toolbox instead, confirming the MCU shows `atmega32u4`.
5. With a browser window focused, press each key and confirm it opens a new tab to the correct URL: `A` → claude.ai, `SO` → stackoverflow.com, `C` → chatgpt.com.

### Flashing on Linux

QMK Toolbox (the GUI flashing tool referenced in Drop's official guide) only ships macOS (`.app.zip`/`.pkg`) and Windows (`.exe`) builds — there is no official Linux binary or AppImage.

On Linux Mint, skip QMK Toolbox and flash directly with `dfu-programmer`, the same tool QMK Toolbox uses under the hood for this board's Atmel DFU bootloader:

```
sudo apt install dfu-programmer
sudo dfu-programmer atmega32u4 erase
sudo dfu-programmer atmega32u4 flash /path/to/3key.hex
sudo dfu-programmer atmega32u4 reset
```

Before flashing, the macropad must be put into bootloader mode by pressing the reset button on the exposed PCB. Reaching that button requires unscrewing the back plate to open the case — you'll need a small screwdriver (Phillips/Torx) for this step.

### Cable note: use USB-A to USB-C, not USB-C to USB-C

This board doesn't power on with a USB-C to USB-C cable — it only works with USB-A to USB-C.

USB-C hosts require a device to present a pull-down resistor on the CC pins before they'll enable VBUS/data. This board's USB-C port appears to skip that resistor, so USB-C hosts never detect it and never power the port. USB-A ports don't do this negotiation — they supply power and data unconditionally — so an A-to-C cable works regardless. This is a hardware limitation of the PCB, not something fixable via firmware.

