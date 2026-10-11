# OTBR deployment reference

The prior base-unit task built and deployed OTBR on a Pi 5 running aarch64 Debian
Trixie. That task later verified service recovery and fresh sensor telemetry.
This publication pass reviewed its saved execution record; it did not connect to
the Pi, export private state, change services or repeat deployment validation.

Sources: [OTBR 65a0ce9f13a5e4d1e0459fb51e68bf087fae5671](https://github.com/openthread/ot-br-posix/tree/65a0ce9f13a5e4d1e0459fb51e68bf087fae5671),
with OpenThread `53e8322140dde7b26827332100504507cec9cc4e`, matching the RCP.

## Recorded build configuration

The successful configuration used **Debug**. Release and MinSizeRel builds failed
on a GCC/MbedTLS array-bounds diagnostic; source, assertions and warning checks
were retained instead of suppressing the diagnostic. Additional recorded development
packages were libmnl-dev 1.0.5-3 and libnftnl-dev 1.2.9-1.

In a separate Linux workspace with required upstream dependencies installed:

```sh
git clone https://github.com/openthread/ot-br-posix.git source
git -C source checkout --detach 65a0ce9f13a5e4d1e0459fb51e68bf087fae5671
git -C source submodule update --init --recursive
test "$(git -C source/third_party/openthread/repo rev-parse HEAD)" = 53e8322140dde7b26827332100504507cec9cc4e
export SOURCE_DATE_EPOCH="$(git -C source show -s --format=%ct HEAD)"
cmake -S source -B build -GNinja \
  -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_INSTALL_PREFIX=/opt/otbr/65a0ce9f13a5e4d1e0459fb51e68bf087fae5671 \
  -DCMAKE_INSTALL_SYSCONFDIR=etc -DINSTALL_SYSTEMD_UNIT=OFF -DBUILD_TESTING=OFF \
  -DOTBR_INFRA_IF_NAME=wlan0 -DOTBR_MDNS=openthread -DOTBR_NFTABLES=ON \
  -DOTBR_DBUS=OFF -DOTBR_FEATURE_FLAGS=OFF -DOTBR_TELEMETRY_DATA_API=OFF \
  -DOTBR_WEB=OFF -DOTBR_REST=OFF -DOTBR_NAT64=OFF -DOTBR_TREL=OFF \
  -DOTBR_BACKBONE_ROUTER=OFF -DOTBR_DHCP6_PD=OFF -DOTBR_DHCP6_PD_CLIENT=none \
  -DOTBR_DNS_UPSTREAM_QUERY=OFF -DOTBR_EPSKC=OFF -DOTBR_NO_AUTO_ATTACH=1 \
  -DOTBR_SRP_SERVER_AUTO_ENABLE=ON -DOT_READLINE=OFF \
  '-DOT_POSIX_SETTINGS_PATH="/var/lib/otbr"' \
  '-DCMAKE_C_FLAGS=-DOPENTHREAD_CONFIG_BORDER_AGENT_UDP_PORT=49191' \
  '-DCMAKE_CXX_FLAGS=-DOPENTHREAD_CONFIG_BORDER_AGENT_UDP_PORT=49191'
cmake --build build --target otbr-agent ot-ctl -j 4
```

This is a configuration reference reconstructed from successful task records,
not a newly tested installer. Review current prerequisites against the pinned source.
Do not run upstream bootstrap/setup scripts on an existing working unit blindly.

## Runtime architecture and recovery

The deployed design uses `otbr-agent.service` and an ordered
`otbr-local-network.service`, with root-protected persistent state. The network
dependency installs the local firewall policy before enabling IPv6 forwarding,
restores IPv6 operation on the infrastructure interface, waits for a valid local
LAN prefix, and retries transient startup failures. A successful recovery starts
the agent. The collector separately retries a missing IPv6 bind address while
keeping its loopback dashboard available.

Only IPv6 forwarding between Thread and the intended local LAN was approved.
IPv4 forwarding, NAT64, WebGUI and REST remain disabled in the recorded deployment.
Port 49191 is the selected border-agent UDP port; access was restricted locally.
The site-specific firewall prefix, interface choices, serial identity, service
environment and prior-state rollback snapshot must be supplied and reviewed locally.
Do not copy a guessed prefix, enable unrestricted forwarding or create a new dataset.

No deployable firewall/service bundle is included: exact site-specific files contain
local network/device information and depend on the original rollback state. To make
a portable installer later, obtain sanitized copies of `network.py`, `guard.nft`,
`agent.env`, both systemd units and the rollback script, then parameterize and test
them on a separate target. The present repository documents the working architecture
without claiming a complete bare-Pi provisioning image.

Thread operational datasets, PSKc, PSKd and joiner entries stay outside version
control. Existing persistent state must survive routine service restarts. The prior
task verified recovery after a dependency restart; this publication did not repeat it.
