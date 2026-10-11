"""Audit generated firmware configuration before considering a flash.

Run against the application's generated zephyr directory, not the sysbuild root.
Does not flash or print any credential material.
"""
from pathlib import Path
import re
import sys

if len(sys.argv) != 2:
    raise SystemExit("Usage: python tools/check_build.py BUILD_APP_ZEPHYR_DIRECTORY")
path = Path(sys.argv[1])
config = (path / ".config").read_text(encoding="utf-8")
dts = (path / "zephyr.dts").read_text(encoding="utf-8")
values = dict(re.findall(r"^(CONFIG_\w+)=(.*)$", config, re.M))
expected = {
    "CONFIG_OPENTHREAD": "y", "CONFIG_OPENTHREAD_SOURCES": "y",
    "CONFIG_OPENTHREAD_FTD": "y", "CONFIG_OPENTHREAD_MANUAL_START": "y",
    "CONFIG_OPENTHREAD_THREAD_VERSION_1_3": "y", "CONFIG_OPENTHREAD_COAP": "y",
    "CONFIG_OPENTHREAD_SLAAC": "y",
    "CONFIG_SHT4X": "y", "CONFIG_I2C": "y", "CONFIG_SETTINGS_ZMS": "y",
    "CONFIG_HWINFO": "y",
    "CONFIG_CSPRNG_ENABLED": "y", "CONFIG_HARDWARE_DEVICE_CS_GENERATOR": "y",
}
failures = [f"{key} is not {value}" for key, value in expected.items() if values.get(key) != value]
for key in ("CONFIG_OPENTHREAD_MTD", "CONFIG_OPENTHREAD_MTD_SED",
            "CONFIG_OPENTHREAD_OPERATIONAL_DATASET_AUTO_INIT",
            "CONFIG_OPENTHREAD_JOINER_AUTOSTART", "CONFIG_OPENTHREAD_SETTINGS_RAM",
            "CONFIG_SHELL_HISTORY", "CONFIG_TEST_RANDOM_GENERATOR", "CONFIG_TEST_CSPRNG_GENERATOR"):
    if values.get(key) == "y":
        failures.append(f"Unexpected enabled feature: {key}")
if values.get("CONFIG_OPENTHREAD_NETWORKKEY", '""') != '""':
    failures.append("A network key is embedded in the build")
if values.get("CONFIG_OPENTHREAD_JOINER_PSKD", '""') != '""':
    failures.append("A joiner credential is embedded in the build")
for text in ("room_sht40", 'compatible = "sensirion,sht4x"', "room_i2c_default"):
    if text not in dts:
        failures.append(f"Missing generated devicetree marker: {text}")
if failures:
    raise SystemExit("FAILED:\n" + "\n".join(failures))
print("PASS: generated configuration audit. Inspect pinctrl and target identity manually before flashing.")
