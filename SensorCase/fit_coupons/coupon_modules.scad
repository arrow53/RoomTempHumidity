// Appended to the unmodified A2 definitions by prepare_fit_coupons.ps1.
// These are cropped test pieces. The production enclosure source is never edited.
fit_part = "overview";
usb_crop_origin = [usb_x-16,-cable_tongue_projection,0];
pcb_crop_origin = [pcb_origin[0],pcb_origin[1]+pcb_holes[0][1]-6,0];
pcb_coupon_hole_xy = [pcb_holes[0][0],6];

module usb_wall_coupon() {
    difference() {
        translate(-usb_crop_origin) intersection() {
            base();
            translate(usb_crop_origin) cube([32,cable_tongue_projection+8,body_depth]);
        }
        // Two edge witness notches mark the unchanged receptacle face plane.
        // They lie outside the swept plug and do not alter the aperture or tongue.
        for(x=[0,30.8]) translate([x,usb_mouth_case[1]+cable_tongue_projection-0.2,floor_thickness-0.4])
            cube([1.2,0.4,0.4+eps]);
    }
}
module pcb_boss_coupon() {
    translate(-pcb_crop_origin) intersection() {
        base();
        translate(pcb_crop_origin) cube([11,12,pcb_origin[2]]);
    }
}
module pcb_thickness_shim() {
    // Thickness dummy only; printed polymer does not reproduce FR4 strength/circuitry.
    difference() {
        cube([11,12,pcb_thickness]);
        translate([pcb_coupon_hole_xy[0],pcb_coupon_hole_xy[1],-eps])
            cylinder(d=pcb_hole_drill,h=pcb_thickness+2*eps);
    }
}
module case_nut_coupon() {
    intersection() {base();cube([11,12,body_depth]);}
}
module case_lid_patch() {
    intersection() {
        lid();
        translate([0,0,-lip_height-eps])cube([11,12,lip_height+lid_thickness+2*eps]);
    }
}
module case_lid_coupon() {
    // Exterior face on the bed, matching the full A2 lid's print orientation.
    translate([0,12,lid_thickness])rotate([180,0,0])case_lid_patch();
}
module coupon_hardware_clearance() {
    union() {
        intersection() {case_nut_coupon();case_hardware();}
        intersection() {pcb_boss_coupon();translate(-pcb_crop_origin)pcb_hardware();}
    }
}

checks();
assert(pcb_width==45 && pcb_height==55 && pcb_thickness==1.6);
assert(abs(case_width-67.8)<0.000001 && abs(case_height-71.8)<0.000001 && abs(case_depth-26)<0.000001);
assert(usb_opening_width==18 && usb_opening_height==10 && abs(usb_face_recess-4.4)<0.000001);
assert(case_nut_pocket_af==5.2 && pcb_support_diameter==6);
if(fit_part=="usb_wall")usb_wall_coupon();
else if(fit_part=="pcb_boss")pcb_boss_coupon();
else if(fit_part=="pcb_shim")pcb_thickness_shim();
else if(fit_part=="case_nut")case_nut_coupon();
else if(fit_part=="case_lid")case_lid_coupon();
else if(fit_part=="usb_sweep_check")intersection(){usb_wall_coupon();translate(-usb_crop_origin)usb_plug_body_sweep(usb_plug_clearance);}
else if(fit_part=="hardware_check")coupon_hardware_clearance();
else if(fit_part=="lid_mating_check")intersection(){case_nut_coupon();translate([0,0,body_depth])case_lid_patch();}
else if(fit_part=="overview") {
    usb_wall_coupon();
    translate([38,0,0])case_nut_coupon();
    translate([54,0,0])case_lid_coupon();
    translate([38,19,0])pcb_boss_coupon();
    translate([54,19,0])pcb_thickness_shim();
}
else assert(false,"Unknown fit coupon selector");
