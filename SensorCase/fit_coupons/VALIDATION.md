# Fit coupon validation

The original 2026-10-10 engineering work reported successful topology checks for
the five new cropped coupons and existing nut coupon, plus three modeled clearance
checks. Raw original logs and reports are not redistributed here.

In this migrated repository, the five primary enclosure meshes and 59 static
enclosure checks passed again. This does not constitute a new print, slicing,
hardware fit, RF or thermal test. The cropped coupons also omit full-enclosure
stiffness and cable routing.

Editable coupon geometry is preserved in fit_coupons_generated.scad and
coupon_modules.scad. Use the existing meshes as prototype samples only; keep all
physical-approval gates false until the real hardware/cable has been measured.

Start with [PRINT_AND_MEASURE.md](PRINT_AND_MEASURE.md) and record physical results
in [measurements.csv](measurements.csv). The supplied worksheet is blank.
