# nRF52840 radio co-processor

This directory records the RCP source pins and build recipe used by the separate
base-unit setup on 2026-10-10. Upstream source, compiler installations and binaries
are not vendored. This publication pass did not rebuild or reflash the radio.

| Item | Recorded value |
| --- | --- |
| Target | nRF52840 DK, UART transport |
| ot-nrf528xx | `1ff0a4905e436eb79605582f36b689063b1282ef` |
| OpenThread | `53e8322140dde7b26827332100504507cec9cc4e` |
| UART | 115200 baud, 8 data bits, no parity, 1 stop bit; RTS/CTS |
| Pins | TX P0.06, RX P0.08, CTS P0.07, RTS P0.05 |

The historical build, image verification and matching-host Spinel compatibility
check succeeded with unmodified upstream source. Recorded HEX SHA-256:
`cd6348fc30c479f5daf7c311f1c108c133dde1bfd64974b4f44be5b8b1bad142`.
This is a historical comparison value, not a guarantee of byte-identical builds
across compilers or host environments. Full compiler/submodule manifests remain
with the original deployment evidence and are not included here.

## Build reference

Use a separate Linux build workspace with Git, CMake, Ninja, an ARM bare-metal
compiler/binutils and newlib already installed. The recorded Debian toolchain used
CMake 3.31.6-2 and gcc-arm-none-eabi 15:14.2.rel1-1. Do not substitute the sensor
node's Nordic SDK version for the RCP toolchain.

```sh
git clone https://github.com/openthread/ot-nrf528xx.git source
git -C source checkout --detach 1ff0a4905e436eb79605582f36b689063b1282ef
git -C source submodule update --init --recursive
test "$(git -C source/openthread rev-parse HEAD)" = 53e8322140dde7b26827332100504507cec9cc4e
cd source
export SOURCE_DATE_EPOCH="$(git show -s --format=%ct HEAD)"
OT_CMAKE_NINJA_TARGET=ot-rcp OT_CMAKE_BUILD_DIR=../build-rcp ./script/build nrf52840 UART_trans -DOT_UART_BAUDRATE=115200
arm-none-eabi-objcopy -O ihex ../build-rcp/bin/ot-rcp ../build-rcp/ot-rcp.hex
```

The matching historical POSIX validation host was built with:

```sh
export SOURCE_DATE_EPOCH="$(git -C openthread show -s --format=%ct HEAD)"
cmake -S openthread -B ../build-host -GNinja -DOT_PLATFORM=posix -DOT_DAEMON=ON -DOT_READLINE=OFF -DBUILD_TESTING=OFF -DCMAKE_BUILD_TYPE=Release -DOT_COMPILE_WARNING_AS_ERROR=ON
cmake --build ../build-host --target ot-daemon -j 4
```

Keep runtime API/capability checks enabled. Identify the actual serial device locally;
the template is `spinel+hdlc+uart:///dev/serial/by-id/<RADIO_IF00>?uart-baudrate=115200&uart-flow-control`.
No flashing/recovery command is provided: those operations must select the actual
board and consider existing contents. No radio change is needed merely to publish.

Sources: [pinned platform](https://github.com/openthread/ot-nrf528xx/tree/1ff0a4905e436eb79605582f36b689063b1282ef),
[pinned OpenThread](https://github.com/openthread/openthread/tree/53e8322140dde7b26827332100504507cec9cc4e).
