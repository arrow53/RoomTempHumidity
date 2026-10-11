# A2 fit coupons: print and measure

Local test files only. Nothing has been printed, uploaded or purchased. The enclosure source, case geometry and PCB interface are unchanged. These samples check fit; they do not approve the ten-board PCBWay build, finished-board fit, RF or thermal performance.

## Files to print

Print one of each at **100% scale, in millimetres**, in the supplied orientation. Use the same printer, material, nozzle, layer height and process intended for the case; record them in the worksheet notes. Inspect the slicer preview before printing. Leave holes, the nut slot and USB passage free of support material. Check bridging at the nut roof and USB roof; do not silently enlarge holes or apply automatic scaling.

| File | Size X x Y x Z, mm | Purpose |
|---|---|---|
| [Existing nut coupon](../provisional_cad/coupon_PROVISIONAL.stl) | 52 x 14 x 8 | Reused, not duplicated. Five pockets: AF 5.0, 5.1, 5.2, 5.3, 5.4 in ascending X. |
| [PCB boss](pcb_boss_PROVISIONAL.stl) | 11 x 12 x 6.4 | Exact crop of A2 floor, support, through-hole and rear screw-head recess. Back face on bed. |
| [Thickness shim](pcb_shim_PROVISIONAL.stl) | 11 x 12 x 1.6 | Optional printed board-thickness dummy; measure its thickness first. Flat on bed. |
| [Case nut pocket](case_nut_PROVISIONAL.stl) | 11 x 12 x 23.6 | Exact corner crop with side-loading nut slot and retaining roof. Back face on bed. |
| [Lid patch](case_lid_PROVISIONAL.stl) | 11 x 12 x 4.8 | Matching corner crop, already exterior-face-down. |
| [USB wall](usb_wall_PROVISIONAL.stl) | 32 x 20 x 23.6 | Exact cropped opening, wall/floor and cable tongue; two added floor-edge datum notches. Floor on bed. |

The original coupon's open pockets check nut size, not roof strength. All five new solids are cropped or derived from the frozen A2 source; there are no alternative case dimensions to choose between.

## Hardware trial

Use the exact hardware specified in [HARDWARE_AND_ASSEMBLY.md](../HARDWARE_AND_ASSEMBLY.md): one M2.5 x 12 DIN 965 countersunk screw, one M2.5 x 8 DIN 912 socket screw, two DIN 934 M2.5 nuts and two DIN 125 A M2.5 washers are enough for the two sample joints.

1. Try the existing coupon pockets. The A2 choice is **5.2 mm AF**. Record which pocket admits and releases the actual nut without forcing. A different winning size is a proposed future revision; do not change A2 automatically.
2. PCB sample: insert the countersunk screw from the back; place the measured 1.6 mm shim on the boss, then washer and nut above it. Align the off-centre holes. A measured 1.6 mm FR4 scrap with a 2.7 mm hole is a better material surrogate. Record rear head proudness, boss height and thread projection. Nominal projection beyond the nut is 1.5 mm. Check for rocking, floor damage and shim bending. Printed polymer does not reproduce PCB strength or circuitry.
3. Lid sample: slide the nut into the side slot. Flip the lid patch into assembly orientation and align its rounded outside corner and screw hole with the base corner; do not rotate it arbitrarily. Fit the socket screw and washer from outside. Check full seating, nut retention under light hand tightening, easy removal, and no roof splitting or screw bottoming. Nominal screw projection below the nut is about 1.1 mm. No torque limit has been qualified.

## USB trial

The tongue points outward. The straight wall's exterior plane is **12 mm from the tongue tip**. The pair of shallow notches at the floor's left/right cut edges marks the receptacle face: **16.4 mm from the tip**, or 4.4 mm behind the exterior plane. The axis is **9.73 mm above the back/floor underside**, not above the inner floor.

Measure the actual plug body width, height, length and its distance from plug tip to body shoulder. At the nominal axis, check body entry and withdrawal without force. The design budget is 16 x 8 mm; the rectangular opening is 18 x 10 mm. The previously reviewed GCT mating drawing still applies, including its 1.85 mm minimum shoulder gap and 6.5 mm illustrated body-height maximum. At that gap, the shoulder is 2.55 mm behind the exterior wall plane.

This sample has no receptacle, PCB locator or cradle. It cannot prove electrical mating, cable bend or finger access in the complete assembly. Once an actual populated board is available, test full mating at the unchanged board location, then check cradle insertion/removal and cable routing. Record actual finished-board thickness and hole fit.

## Record and stop conditions

Fill [measurements.csv](measurements.csv); blank cells mean unmeasured. Use calipers, a straightedge and the actual hardware/cable. Photograph the setup if useful. Record filing, drilling or other cleanup separately because it changes the test result. Stop on binding, a proud rear screw head, rocking, cracking, PCB/shim bowing or incomplete mating. Keep fit/RF/thermal approval gates false until the full assembly is checked.

Reproduction: run `prepare_fit_coupons.ps1`, then `validate_coupon_meshes.py` with Python 3. See [VALIDATION.md](VALIDATION.md) for digital checks and limits.
