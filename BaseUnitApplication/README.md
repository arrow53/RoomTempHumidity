# Pi collector and dashboard

Python collector, SQLite history and a loopback-only browser dashboard. The source
includes receiver retry behavior so the UI remains available while a Thread address
is missing. The prior integration work reached live telemetry; this repository has
no household database, room mapping, device identifiers or live bind address.

## Local preview and tests

Use Python 3.11+ from this directory:

```sh
python -m venv .venv
# Activate .venv using the command for your shell, then:
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m room_monitor --mode demo
```

Open `http://127.0.0.1:8080`. Demo data is explicitly labelled and stored separately.
The tests use local TCP/IPv6 UDP sockets and temporary databases; restricted sandboxes
may block or stall these tests. All 26 passed on Windows with loopback access allowed.

## Live configuration

Copy `config/rooms.example.json` to ignored `config/rooms.json`, replacing example
IDs/labels with verified node IDs and desired room names. Keep this local. Start with
`python -m room_monitor --mode live`; defaults bind CoAP to IPv6 loopback.
For actual Thread traffic, supply the Pi's verified reachable IPv6 address using
`--coap-host <PI_IPV6> --allow-lan-coap`. Never use guessed or example live addresses.
HTTP stays on loopback. No application-layer authentication is claimed for CoAP;
limit receiver reachability to the intended local network.

`deploy/room-monitor.service.example` is a user-service template, not an installed
unit. Adjust its working directory, Python path and receiver options to the local
checkout. Do not replace a running service before preserving its existing settings.
For display use, open the local URL in the Pi's browser; kiosk/autostart and touch
rotation depend on the actual desktop/display configuration and are not auto-installed.

See [OTBR deployment reference](OTBR.md) and the
[radio firmware reference](../BaseUnitFirmware/README.md). The source snapshot does
not contain a complete OS image or a site-independent installer.
