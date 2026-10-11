# Sensor firmware

nRF54L15 DK prototype with an SHT40 at I2C address 0x44, continuously USB-powered.
Samples every 60 seconds and reports confirmable CoAP readings with a random boot
ID and per-boot sequence. The custom sensor PCB requires its own verified board
configuration and bring-up; the DK overlay is not a production-board definition.

The application pins Nordic nRF Connect SDK v3.2.1 through `west.yml`. Install that
SDK and its matching toolchain separately; SDK/toolchain distributions are not
included. In its configured terminal, from this directory:

```sh
west build -b nrf54l15dk/nrf54l15/cpuapp --sysbuild -d build .
python tools/run_host_tests.py
```

The host runner always runs schema tests and runs C tests when a host C compiler
is available. Full target builds, sensor wiring and real hardware checks are separate.
The publication pass reran 12 schema tests; historical target-build success is not
a fresh target rebuild of this moved checkout.

For a configured collector, copy `config/collector.conf.example` to ignored
`local.conf` and set the real routed unicast collector address locally. Inspect the
board overlay and wiring before use. Build with explicit local configuration:

```sh
west build -p always -b nrf54l15dk/nrf54l15/cpuapp --sysbuild -d build . -- -DEXTRA_CONF_FILE=local.conf -DDTC_OVERLAY_FILE=boards/nrf54l15dk_nrf54l15_cpuapp.overlay
```

`-p always` recreates the selected build directory. No dataset, PSKd or network key
belongs in a build definition. An uncommissioned device does not create a new Thread
network. Provision privately through an authorized per-device commissioner or trusted
physical console; terminal recordings may expose provisioning values. Stored Thread
settings persist across ordinary reboot; full erase/recovery removes them. The
application does not provide signed updates, debug locking or collector authentication.

The JSON schema and shared reboot/replay vectors are under `protocol/` and mirrored
in BaseUnitApplication. Their placeholder/example IDs are not deployment identifiers.

See [DK wiring](docs/wiring.md) before connecting the breakout.
