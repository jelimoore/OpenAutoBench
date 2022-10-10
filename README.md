# OpenAutoBench

## THIS SOFTWARE IS DEPRECATED. DO NOT USE THIS. SEE NEW VERSION AT https://github.com/jelimoore/OpenAutoBench-ng

An open source project for automatically testing and tuning land mobile radios and infrastructure.

## Notes, warnings, etc

Warn: This is beta software. Things are prone to breaking. Do not use this in a mission critical or life safety application.

Note: This is not a replacement for a test set with built in auto tuning functionality. Additionally, no digital modulation tests can be performed. Only analog tests are supported (mod balance, reference oscillator, measured power, front end filter, etc).

Note: This is not a magic wand. You as the operator should still be familiar with manual tuning procedure for your radio. Again, this is not a replacement for a test set with built in auto tuning. **THIS PROGRAM WILL NOT DO YOUR JOB FOR YOU.** This is simply meant to be a helper, of sorts, except virtual.

Note: Many radios will likely not be supported (and certain model numbers within a family may work while others don't). If you want support for your radio, you can either open an issue and be patient, or clone the repo, code the tests yourself, and make a PR. The author only has so many radios at her disposal to test with.

Note: There is a difference between auto*test* and auto*tune* in this program. Autotest is for verifying a radio's performance without adjusting any softpots. Autotune will automatically tune the radio and bring it into spec. For example, some tests may not have full autotune support yet, and they will just test the radio's performance against spec. You as the operator will always have control over whether to test or align a radio.

Note: Currently, autotune is not supported, and likely won't be for a while. Currently, it will just test radios.

Note: GPIB is an old standard (parallel bus, yuck). You will likely need an adapter that goes from your test set to your computer. You can either purchase a commercial adapter, or use the open-source (AR488)[https://github.com/Twilight-Logic/AR488] adapter. It can be built with just an Arduino and a Centronics 24-pin connector.

## Radios and Tests

The platform supports many radios including Motorola APX, XPR, Astro25; and DVMProject hotspots and repeater modems.

Tested Platforms:
- APX
  - APX900 (U)
  - APX7000 (V/7/8)
  - APX8000 (all)
- MotoTRBO
  - XPR6350 (T)
  - XPR4550 (Q)
  - XPR5550 (Q)
- Astro25
  - XTS5000 (Q, K)
  - XTL1500/2500/5000/Astro Digital Consolette family (U, K)
- Quantar
  - Quantar (800MHz)
- DVMProject
  - MMDVM_HS_Dual
  - STM32F4_POG (Repeater-Builder)

## Test Sets and Instruments

The platform supports many different vendor-agnostic interfaces such as GPIB and SCPI. You have a choice of GPIB or SCPI, over either ethernet or serial. For example, you could have an ethernet to GPIB converter, USB/serial to GPIB converter, raw TCP/SCPI to an instrument, or USB/serial to an instrument that speaks SCPI. Simply set the appropriate options in config.yml.

## License

This is licensed under the GNU GPLv3 license. Use of this project is intended for amateur and/or educational use ONLY. Any other use is at the risk of user and all commercial purposes are strictly discouraged.

All product names, logos, brands, trademarks and registered trademarks are property of their respective owners.

Copyright (C) Natalie Moore 2022

## Setup and testing

Good luck. I still need to document this. Set up config.yml, run the OpenAutoBench.py file and play around.
