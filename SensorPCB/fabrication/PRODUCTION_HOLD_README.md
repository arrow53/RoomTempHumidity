# Room sensor A3-Q10 - ten-board quote and DFM package

Prepared 2026-10-10. **Use A3 files together for the current quotation. A2 is superseded and retained only as history. QUOTE / DFM ONLY: fabrication, assembly, order and payment are not authorized.** Return the itemized quote and engineering questions for review. Any subsequent manufacturing-file change requires a new package version and hashes.

The board uses a Raytac AN54LQ-P15 nRF54L15 module with integrated antenna, an onboard SHT40-AD1B-R3 sensor, and USB-C 5 V power. U3 is now **Analog Devices LT1761IS5-3.3#TRMPBF**, with reverse-current protection. The BOM permits the identical #TRPBF packaging variant. No other regulator or manufacturer is an approved substitute. A3 updates U3's land pattern and its local input/shutdown trace loop; component centres, enclosure interface, RF keepout and all other pad geometries are unchanged.

## Files and quote settings

- `fabrication/`: seven Gerbers (two copper, two mask, two silk, one outline), separate PTH/NPTH Excellon drills and drill maps. Common lower-left origin, X right, Y up, millimetres. The two internal sensor slots are unplated CNC-routed contours in Edge.Cuts. The four USB shell-anchor slots are plated and in the PTH file.
- `assembly/BOM-10-boards.csv`: 16 populated references, 13 unique MPNs. Each row has quantity per board 1 and total for ten boards 10. Map the per-board field to the portal; do not multiply the ten-board total again. Quote feeder wastage separately; no full-reel purchase is authorized.
- `assembly/CPL-top-mm.csv`: 16 TOP body-centre placements, counterclockwise degrees. J1 body centre is (22.500,3.675), mouth toward negative Y. Its native footprint origin is at the mouth (22.500,0.000), which is not the body centroid. Use the supplied CPL.
- `assembly/`: schematic, native and enlarged orientation PDFs, paste Gerber, DNP list and handling/test instructions. Match feeder orientation to the drawing, not a guessed machine-library zero.
- `verification/`: native ERC/DRC/netlist, independent CAM/drill/paste/placement/BOM audits and exported-layer previews.
- `editable/`: portable KiCad 10 project and local libraries. Open `room_sensor.kicad_pro`. No construction board or obsolete preview is included.

**10 finished individual PCBs and 10 turnkey assembled units; 45 x 55 mm; 2 layers; 1.6 mm finished FR-4; Tg >=150 C; 1 oz finished outer copper; ENIG; green solder mask both sides; white silkscreen; lead-free/RoHS; no controlled impedance; all vias tented both sides; electrical bare-board test required.** Only TOP has components. J2 is DNP bare SWD access; test points and holes are PCB features, not purchased parts. No battery or USB data circuit.

No board wash, coating or potting. Follow the SHT40 handling document. The assembler may propose panel rails/fiducials, subject to drawing review; deliver individual boards. No tabs on the antenna edge, either sensor slot or the 1 mm sensor edge web. Depanel without stressing the sensor. No unapproved land/outline/keepout changes.

## Remaining production holds

1. **Supplier USB DFM acceptance:** accept J1's 0.1751 mm nominal pad-to-locating-hole clearance, GCT's +/-0.05 mm recommended-layout tolerance, combined finished-hole/registration/etch tolerances, 0.100 mm mask dams and finished plated-slot fit. See `USB_DFM_QUESTION.txt` for exact coordinates and the unsent question. KiCad's scoped 0.15 mm clearance rule does not establish factory capability; return a proposed correction if needed.
2. **Sourcing/process agreement:** confirm genuine AN54LQ-P15 availability, exact MPNs/allowed packaging variants, traceable lots, feeder wastage, module dry-pack/floor-life handling, compatible reflow, stencil and hidden-joint inspection. The module procurement code is MD-240A8-002. No unapproved substitutions or assumed full-tray/reel purchase.
3. **Programming/test scope:** agree factory programming/testing versus assembled boards for owner programming. No custom-module image/hash, selected fixture or credentials are supplied. The DK image and Raytac factory firmware are not automatically suitable for this carrier. A fully assembled quote must identify programming/testing inclusion or exclusion explicitly.

The previously unexamined capacitor derating and regulator reverse-current design items are addressed in A3. `POWER_REVIEW.pdf` records the source-based capacitor screen, protected regulator and operating conditions. These desk calculations are not measured hardware qualification. Keep the 3.3 V design load within 50 mA, heater off, and verify the chosen supply/cable and input headroom. Do not advertise 100 mA board output across arbitrary USB conditions merely because the regulator has that device rating.

## Physical qualification after an approved prototype build

The custom board has not been fabricated or measured. Test startup, load steps, rail ripple and repeated power removal; supply/cable/fuse temperature and input headroom; post-reflow humidity accuracy and regulator/radio heating; RF in the final enclosure; USB fit/retention, fasteners and slot/web strength; and ESD. No working DK result closes those custom-board checks. Review the prototype results before deploying the batch.

Enclosure coordinates remain upper-left X-right/Y-down: mounting holes (4,18),(4,49),(41,49), 2.7 mm NPTH; USB mouth (22.5,55); sensor (39,38). Convert to manufacturing with (x,55-y). PCB antenna copper exclusion remains full-width y=0..3.4 mm; the enclosure no-metal reserve remains y=0..12 mm.

## Verification and references

Native ERC/DRC: zero findings, unconnected items or schematic parity issues; no DRC exclusions. ERC retains four factory advisory ignores recorded in the report. Independent Gerbonara checks cover 105 copper pad centres, 48 vias, 58 circular plated holes plus four plated slots, five NPTH holes, three closed edge contours, 87 paste apertures, all 16 BOM/CPL rows and U3 copper/mask/paste dimensions. All component centres and rotations match A2. Gerbonara's warning about KiCad's G90 drill-header placement is retained; parsed drill coordinates and diameters match the native geometry.

- [Raytac module v1.2](https://www.raytac.com/download/index.php?index_id=74) and official design guide 260921, included locally.
- [ADI LT1761 Rev F](https://www.analog.com/media/en/technical-documentation/data-sheets/1761sff.pdf), [current order models](https://www.analog.com/en/products/lt1761.html), and included official S5 package drawing.
- [GCT USB4105 drawing](https://gct.co/files/drawings/usb4105.pdf), included locally.
- Sensirion SHT4x v7.3 and handling instructions v9, included locally; remaining exact part references are in the BOM.
- [PCBWay capabilities](https://www.pcbway.com/capabilities.html). Written supplier acceptance of the specified exceptions remains required.
