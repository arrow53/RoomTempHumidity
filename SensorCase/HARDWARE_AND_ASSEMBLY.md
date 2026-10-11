# A2 prototype hardware and assembly

Dimensions are millimetres. Hardware is selected by standard and envelope; no purchase or assembly has occurred. Actual supplier parts, tolerances and printed fits must be checked. Use removable metal nuts and screws; there are no printed threads or heat-set inserts in A2.

## Bill of materials

| Qty | Part | Modeled envelope / use |
|---:|---|---|
| 3 | DIN 965 M2.5 x 12 countersunk cross-recess screws, pitch 0.45 | 12 overall length including head; head diameter 4.7, height 1.5. PCB mounting from exterior back. |
| 4 | DIN 912 / ISO 4762 M2.5 x 8 socket-head screws, pitch 0.45 | 8 under-head length; head diameter 4.5, height 2.5; 2 mm hex drive. Lid closure. |
| 7 | DIN 934 M2.5 hex nuts | 5 across flats, 2 height; three above PCB, four side-loaded into case bosses. |
| 7 | DIN 125 A M2.5 flat washers | 2.7 ID x 6 OD x 0.5; three above PCB, four outside lid. |

The screw-head dimensions follow [Fuller's DIN 965 table](https://fullerfasteners.com/tech/din-965-specifications-cross-recessed-countersunk-head-screws/) and [Engineering Hardware's M2.5 socket-head specification](https://engineeringhardware.com/guide/size/m2.5-socket-head-cap-screws/). The maximum nut envelope follows the M2.5 row in [Fasteners By Design's DIN 934 specification](https://fastenersbydesign.com/wp-content/uploads/Spec-Sheets/Metric-Nut-Finished-Hex-DIN-934.pdf), pp. 1–2. The washer dimensions match [Spaenaur 657-068](https://spaenaur.com/products/657-068). These are dimensional references, not a plastic-joint torque qualification.

Use the specified DIN 965 head envelope: a generic M2.5 countersunk screw from another standard can have a different head. The wall mounting screws and anchors are separate, substrate-dependent hardware; the existing 6.8 mm entry / 3.6 mm neck keyholes and 4 mm spacers are retained. Their actual head fit and retention remain to be checked.

## PCB mounts

Each actual PCB hole receives a 6 mm diameter, 4 mm high support integral with the back floor. A 2.9 mm through-bore gives clearance for the M2.5 shank; the PCB's existing 2.7 mm NPTH holes are unchanged. A back-side tapered head recess is 5.4 mm at its mouth and 1.6 mm deep. It is a clearance envelope rather than an exact countersink-tool profile. Verify that the chosen screw seats flush or below the back surface.

The PCB underside is at case Z=6.4 and top at Z=8.0. Each washer occupies Z=8.0..8.5; its nut Z=8.5..10.5. A nominal 12 mm screw tip ends at Z=12, leaving 1.5 mm beyond the nut. The washer and nut stay within the handoff's 6 mm mounting reservation. Threads, end chamfers, drive recesses and supplier length tolerances are not modeled.

The force path is back screw head → printed floor/support → PCB → washer/nut. Tighten gently by hand while supporting the boss; do not bow the PCB, crush the floor or apply a metal-joint torque specification. The 0.8 mm floor thickness below the deepest recess and the printed supports require physical strength and creep checks.

## Removable lid

The four 9.2 mm case bosses have 5.2 mm AF, 2.2 mm deep nut pockets with a nominal 2 mm retaining roof. Load each nut laterally from the cavity, with its flats parallel to the slot walls, before placing the lid. The roof retains the nut under screw load. No nut is expected to clamp from an unretained top-entry pocket. With the lid removed, keep the base level because an unengaged nut can slide back out.

The nominal washer sits at Z=26..26.5; the socket head ends at Z=29. Each 8 mm screw tip ends at Z=18.5, extending about 1.1 mm below the seated nut without bottoming in the clearance bore. The lower washers/heads are accommodated by 7.2 mm diameter reliefs in the cradle's front guides. The lid lip has 0.3 mm clearance per side and needs a print-fit check.

## Cable envelope

The [GCT USB4105 drawing B4](https://gct.co/files/drawings/usb4105.pdf), mating view on sheet 2, shows a minimum 1.85 mm gap from receptacle front to plug-body shoulder and a maximum 6.5 mm plug-body height for the illustrated mating profile. The original engineering review used the manufacturer drawing; the vendor PDF is not redistributed here. A2's larger 16 x 8 mm body gauge is a conservative enclosure-access budget, not permission to violate the connector's mating profile.

The access test sweeps the enlarged body gauge to the receptacle face. The separate cradle test uses the GCT shoulder offset, a 20 mm body and 8 mm extra withdrawal travel, all with 0.5 mm gauge clearance. The body can pass through the aperture without moving the PCB. Cable exit, connector latch action, grip access, overmold length, flexible cable bending and tie placement still need a selected cable and physical assembly.

## Assembly trial

Small hardware and USB samples are now prepared: follow [the coupon print/measurement guide](fit_coupons/PRINT_AND_MEASURE.md) before the full assembly trial below. The original five-pocket coupon is reused, and the new side-load nut/roof and PCB boss samples reproduce actual A2 geometry.

1. Print and measure the coupon first. Its five nut pockets run left to right at X=6,16,26,36,46 with AF=5.0,5.1,5.2,5.3,5.4. Each has the 2.9 mm bore and the same back head recess. Choose a removable fit for the actual nut; update the source if needed. The open coupon pockets do not prove the case's side-loading roof strength or bridging quality.
2. Slice the base back-face-down, lid exterior-face-down and cradle bed-down. Inspect the nut-roof bridges, USB 6 mm bridge, vents, recesses and wall continuity. No printer/material/process has been qualified.
3. Insert the three PCB screws from the rear. Lower the PCB onto all three supports without contacting the sensor island/slots, then add the three washers and nuts. Verify no head protrudes behind the case and no washer reaches circuitry outside its mounting reserve.
4. Side-load the four case nuts, place the lid, and fit the four lid screws with washers. Check that the lid seats without force and remains removable for SWD/pogo access.
5. Check the actual cable through the opening, both outside and inside the cradle. Verify cradle insertion/removal, screw-head reliefs and cable bend. Test wall mounting separately with selected wall hardware.
6. Check support/clamp strength, sensor-slot webs, sensor bias/response and radio performance with the final board and selected hardware. Keep all final approval gates false until those checks are completed.
