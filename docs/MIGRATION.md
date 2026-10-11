# Canonical workspace migration

Future tasks must use `C:\GIT\RoomTempHumidity` and read AGENTS.md.
`C:\CodexTemp` is preserved as an untouched legacy backup.

| Legacy source | Canonical location |
| --- | --- |
| sensor-firmware | SensorFirmware |
| enclosure_A2 | SensorCase |
| room-sensor-pcb/manufacturing/A3-Q10/editable | SensorPCB/editable |
| Current A3 selected fabrication and assembly files | SensorPCB/fabrication and SensorPCB/assembly |
| Separate base-unit RCP task | BaseUnitFirmware source/build reference |
| roomlight-dashboard | BaseUnitApplication |
| Separate base-unit OTBR task | BaseUnitApplication/OTBR.md |
| pi-display-enclosure/outputs | BaseUnitCase/snapshot-prototype-A (paused) |

No Git histories existed in the source trees. Historical revisions and original
quote archives stay in the legacy backup. Editable firmware, application, native
KiCad, sensor OpenSCAD and paused base-case source are present.

## External dependencies and completeness limits

- Install Nordic NCS v3.2.1 with its matching toolchain separately.
- Fetch RCP/OTBR and recursive submodules at their documented immutable pins.
  Build recipes reflect historical successful execution, not a fresh rebuild.
- Install OpenSCAD separately; use OPENSCAD_EXE or -OpenScadPath.
- Use KiCad for the project-local CAD. Vendor PDFs, Raytac/KiCad STEP bundles and
  assembled STEP exports are held pending redistribution review. Complete component
  3D visualization is not included.
- Selected A3 files are quote/DFM material, not a full reviewed order package.
  Old PCB generators are historical iteration tools and are not portable rebuild
  entry points for current native CAD.
- Household mappings, databases, datasets, device identities and raw deployment
  records are omitted. Exact OTBR firewall/service/rollback files need sanitized,
  parameterized versions before this becomes a fresh-Pi installer.
- BaseUnitCase is an incomplete paused prototype, not a validated enclosure.

Saved task prompts/shortcuts still targeting old directories must be updated by
their owners. This repository does not silently alter other tasks or services.
