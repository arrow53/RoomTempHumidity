# DK prototype wiring

This reference applies to the PCA10156 revision 1.0.0 nRF54L15 DK and Adafruit
4885 SHT40 breakout, not the custom bare-sensor PCB.

| Signal | Breakout | DK header P1 |
| --- | --- | --- |
| SDA | SDA | Contact 14 / GPIO P1.11 |
| SCL | SCL | Contact 15 / GPIO P1.12 |
| Ground | GND | Contact 2 / GND |
| Power | VIN | Contact 1 / VDD:IO, after confirming 3.3 V |

Physical contact numbers differ from printed GPIO labels. Confirm the board revision,
connector orientation and actual voltage using the manufacturer's documentation.
The overlay uses I2C21 at 100 kHz. The DK's default logic supply may be 1.8 V; this
breakout arrangement requires the verified 3.3 V configuration. Disconnect power
before wiring. Do not connect 5 V pull-ups to DK GPIOs or back-feed the breakout's
3V regulator output. Custom PCB supply/pull-up/thermal design is separate.

Reference: Nordic PCA10156 revision 1.0.0 schematic, connector sheet 7, from the
[official hardware archive](https://nsscprodmedia.blob.core.windows.net/prod/software-and-other-downloads/dev-kits/nrf54l15-dk/pca10156-nrf54l15-dk-1_0_0.zip).
No vendor illustration or live device serial is redistributed here.
