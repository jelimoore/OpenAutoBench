# OpenAutoBench

An open source project for automatically testing and tuning land mobile radios and infrastructure.

## Notes, warnings, etc

Warn: This is beta software. Things are prone to breaking. Do not use this in a mission critical or life safety application.

Note: This is not a replacement for a test set with built in auto tuning functionality. Additionally, no digital modulation tests can be performed. Only analog tests are supported (mod balance, reference oscillator, measured power, front end filter, etc).

Note: This is not a magic wand. You as the operator should still be familiar with manual tuning procedure for your radio. Again, this is not a replacement for a test set with built in auto tuning. **THIS PROGRAM WILL NOT DO YOUR JOB FOR YOU.** This is simply meant to be a helper, of sorts, except virtual.

Note: Many radios will likely not be supported (and certain model numbers within a family may work while others don't). If you want support for your radio, you can either open an issue and be patient, or clone the repo, code the tests yourself, and make a PR. The author only has so many radios at her disposal to test with.

Note: There is a difference between auto*test* and auto*tune* in this program. Autotest is for verifying a radio's performance without adjusting any softpots. Autotune will automatically tune the radio and bring it into spec. For example, some tests may not have full autotune support yet, and they will just test the radio's performance against spec. You as the operator will always have control over whether to test or align a radio.

Note: Currently, autotune is not supported, and likely won't be for a while. Currently, it will just test radios.

Note: HPIB is an old standard (parallel bus, yuck). You will likely need an adapter that goes from your test set to your computer. You can either purchase a commercial adapter, or use the open-source (AR488)[https://github.com/Twilight-Logic/AR488] adapter. It can be built with just an Arduino and a Centronics 24-pin connector.

## License

This is licensed under the GNU GPLv3 license. Use of this project is intended for amateur and/or educational use ONLY. Any other use is at the risk of user and all commercial purposes are strictly discouraged.

Copyright (C) Natalie Moore 2022

## Setup and testing

Good luck. I still need to document this. Just run the OpenAutoBench.py file and play around.

As this is beta, a lot of things are assumed. Namely, if your HPIB interface is on a different serial port, or your radio is a different IP address, you will need to modify the code.