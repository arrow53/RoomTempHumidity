// Generated from unchanged A2 SHA256 041B124A54741B798A7EEE065F5A520A0DF61F70BC907027BBFCC83D8A72B8EA
/*
ROOM SENSOR ENCLOSURE / prototype A2 / PCB A1 routed, dimensions unchanged / 2026-10-10
Units: mm. EDITABLE PROVISIONAL SOURCE, not a manufacturing release.
The 45 x 55 PCB and feature coordinates follow the provisional PCB A1 handoff.
No fit approval or manufacturer 3D antenna/plastic keepout is implied.
See README.md and mechanical_interface.json before changing release gates.

Axes in the enclosure: X = right, Y = up when installed, Z = back to front.
Base exterior back plane Z=0. USB exits -Y. Lid exterior faces +Z.
OpenSCAD F5 previews; F6/export requires explicit provisional acknowledgement.
No external libraries required. OpenSCAD 2021.01 language subset.
*/

/* [View] */
part = "assembly"; // [assembly,exploded,base,lid,stand,shelf_assembly,wall_spacer,coupon]
show_reference_board = true;
show_keepouts = true;
show_hardware = true;
exploded_gap = 16;

/* [Release status -- do not change without mechanical review] */
mechanical_interface_confirmed = false;
acknowledge_provisional_render = false;
antenna_review_confirmed = false;
pcb_supports_confirmed = false;
prototype_supports_authorized = true; // permits A2 prototype mounts; no final fit approval
thermal_baffle_confirmed = false;

/* [PCB A1 routed handoff -- not frozen or fit approved] */
pcb_width = 45;
pcb_height = 55;
pcb_thickness = 1.6;
side_margin = 9;
bottom_margin = 2;
top_margin = 10;
pcb_support_height = 4;
component_height_top = 6; // reserve for DNP/pogo SWD; fitted header may need more
component_height_bottom = 2;

/* [FDM shell] */
wall = 2.4;
floor_thickness = 2.4;
body_depth = 23.6;
lid_thickness = 2.4;
corner_radius = 4;
lip_height = 2.4;
lip_thickness = 1.2;
lip_clearance = 0.3; // per side; tune by coupon
eps = 0.02;
$fn = 48;

/* [Case fasteners -- independent of PCB holes] */
enable_case_fasteners = true;
case_boss_diameter = 9.2;
case_boss_x_from_edge = 6;
case_screw_bottom_y = 6; // below relocated sensor vents and optional baffle
case_screw_top_offset = 30; // entire boss stays below provisional RF band
lid_screw_clearance = 2.9;
case_nut_pocket_af = 5.2; // M2.5 DIN 934 nut; print-fit coupon required
case_nut_pocket_depth = 2.2;
case_nut_roof = 2; // load-bearing roof over side-loaded captive nut
case_screw_length = 8; // M2.5x8 socket head, length under head
screw_relief_diameter = 2.9;
screw_relief_depth = 10;

/* [PCB mounting -- removable prototype through-bolts in unchanged A0 holes] */
enable_pcb_supports = true;
pcb_holes_top_view = [[4,18],[4,49],[41,49]]; // PCB upper-left origin, Y down
pcb_hole_drill = 2.7; // NPTH clearance for proposed M2.5 hardware
pcb_support_diameter = 6; // stays within handoff boss reservation
pcb_support_clearance = 2.9;
pcb_screw_length = 12; // DIN 965 M2.5x12, overall countersunk length
pcb_head_pocket_diameter = 5.4;
pcb_head_pocket_depth = 1.6; // conservative head envelope; verify flushness on coupon
fastener_thread_diameter = 2.5;
fastener_pitch = 0.45;
fastener_nut_af = 5;
fastener_nut_height = 2;
fastener_washer_od = 6;
fastener_washer_id = 2.7;
fastener_washer_thickness = 0.5;
pcb_head_diameter = 4.7;
pcb_head_height = 1.5;
case_head_diameter = 4.5;
case_head_height = 2.5;

/* [USB opening -- placeholder plug envelope] */
usb_mouth_top_view = [22.5,55];
usb_center_above_pcb_top = 1.73;
usb_shell_width = 8.94;
usb_shell_depth = 7.35;
usb_shell_height = 3.31;
usb_opening_width = 18;
usb_opening_height = 10;
usb_roof_flat_width = 6; // 45-degree shoulders and short bridge; check in slicer
usb_plug_body_width_budget = 16; // design envelope, not a selected cable
usb_plug_body_height_budget = 8; // deliberately exceeds GCT mating sketch's 6.5 mm body
usb_plug_clearance = 0.5; // checked swept-body margin; nominal aperture margin is 1 mm
usb_plug_body_length_budget = 20;
usb_insertion_travel_budget = 8;
usb_mated_body_gap = 1.85; // GCT B4 mating sketch: body shoulder to receptacle front minimum
enable_cable_tongue = true;
cable_tongue_width = 24;
cable_tongue_projection = 12;
cable_tie_slot_width = 2.2;
cable_tie_slot_length = 4;
cable_tie_slot_spacing = 12;

/* [Sensor air path -- right-side PCB A0 island] */
sensor_top_view = [39,38];
sensor_body_width = 1.5;
sensor_body_height = 0.5;
sensor_minimum_free_air = 2;
sensor_island_top_view = [[33,31],[44.5,45]]; // reserve island and implemented A1 L slots/webs
sensor_vent_width = 7.2;
sensor_vent_length = 12;
sensor_side_vent_z = 12;
vent_slot_width = 2.4;
vent_pitch = 4.8;
enable_sensor_baffle = false; // only after component/thermal-island review
baffle_thickness = 1.6;
baffle_pcb_gap = 1;
sensor_baffle_island_gap = 1;

/* [Wall attachment -- metal locations require antenna review] */
enable_wall_keyholes = true;
wall_keyhole_x_from_edge = 6;
wall_keyhole_entry_y = 29;
wall_keyhole_travel = 6;
wall_keyhole_entry_diameter = 6.8;
wall_keyhole_neck = 3.6;
wall_spacer_height = 4;
wall_spacer_diameter = 10;

/* [Shelf cradle -- plug and bend clearance are provisional] */
stand_side_extension = 8;
stand_depth_extension = 24;
stand_base_thickness = 3;
stand_under_case_clearance = 30;
stand_guide_height = 8;
stand_fit_clearance = 0.4; // per side
stand_pedestal_width = 11;
stand_rail_thickness = 3;
stand_screw_relief_diameter = 7.2;

/* [Antenna keepout -- exact manufacturer requirement required] */
// A list of [[x,y,z],[width,height,depth]] boxes in enclosure coordinates.
// Empty means UNKNOWN, not zero clearance. Include cable/hardware keepouts.
antenna_keepout_boxes = [];

/* [PCB A0 module and separate provisional RF reservation] */
module_top_view_origin = [17.75,0];
module_size = [9.5,13.7,1.8]; // Raytac AN54LQ-P15 per PCB handoff
rf_reservation_top_view = [[0,0],[45,12]]; // NO METAL/CABLE; NOT manufacturer 3D rule
pcb_copper_keepout_depth = 3.3; // PCB-only rule per sibling; enclosure RF/plastic review stays open

/* [Derived geometry] */
case_width = pcb_width + 2*side_margin + 2*wall;
case_height = pcb_height + bottom_margin + top_margin + 2*wall;
case_depth = body_depth + lid_thickness;
pcb_origin = [wall + side_margin, wall + bottom_margin, floor_thickness + pcb_support_height];
function pcb_top_to_local(p) = [p[0],pcb_height-p[1]];
function pcb_top_to_case(p,z=0) =
    [pcb_origin[0]+p[0],pcb_origin[1]+pcb_height-p[1],pcb_origin[2]+pcb_thickness+z];
pcb_holes = [for(p=pcb_holes_top_view) pcb_top_to_local(p)];
usb_mouth_case = pcb_top_to_case(usb_mouth_top_view,usb_center_above_pcb_top);
usb_x = usb_mouth_case[0];
usb_z = pcb_origin[2] + pcb_thickness + usb_center_above_pcb_top;
usb_face_recess = usb_mouth_case[1]; // unchanged 4.4 mm; A2 lets the plug body enter this recess
usb_roof_rise = (usb_opening_width-usb_roof_flat_width)/2;
pcb_nut_bottom_z = pcb_origin[2]+pcb_thickness+fastener_washer_thickness;
case_nut_bottom_z = body_depth-case_nut_roof-case_nut_pocket_depth;
case_nut_seated_z = body_depth-case_nut_roof-fastener_nut_height;
sensor_case = pcb_top_to_case(sensor_top_view,sensor_body_height);
sensor_island_min = pcb_top_to_case([sensor_island_top_view[0][0],sensor_island_top_view[1][1]]);
sensor_island_max = pcb_top_to_case([sensor_island_top_view[1][0],sensor_island_top_view[0][1]]);
sensor_vent_x = sensor_case[0]-vent_slot_width/2;
sensor_vent_y = sensor_case[1]-sensor_vent_length/2;
sensor_bay_left_x = sensor_island_min[0]-sensor_baffle_island_gap-baffle_thickness;
sensor_bay_bottom_y = sensor_island_min[1]-sensor_baffle_island_gap-baffle_thickness;
sensor_bay_top_y = sensor_island_max[1]+sensor_baffle_island_gap+baffle_thickness;
module_case_origin = pcb_top_to_case([module_top_view_origin[0],module_top_view_origin[1]+module_size[1]]);
rf_reservation_min = pcb_top_to_case([rf_reservation_top_view[0][0],rf_reservation_top_view[1][1]]);
rf_reservation_size = [rf_reservation_top_view[1][0]-rf_reservation_top_view[0][0],
                      rf_reservation_top_view[1][1]-rf_reservation_top_view[0][1],case_depth];
// Full enclosure depth is our conservative visualization extrusion, not a vendor Z limit.
rf_reservation_boxes = [[[rf_reservation_min[0],rf_reservation_min[1],0],rf_reservation_size]];
case_fastener_xy = [
    [case_boss_x_from_edge,case_screw_bottom_y],
    [case_width-case_boss_x_from_edge,case_screw_bottom_y],
    [case_boss_x_from_edge,case_height-case_screw_top_offset],
    [case_width-case_boss_x_from_edge,case_height-case_screw_top_offset]
];
wall_keyhole_xy = [[wall_keyhole_x_from_edge,wall_keyhole_entry_y],
                  [case_width-wall_keyhole_x_from_edge,wall_keyhole_entry_y]];
stand_width = case_width + 2*stand_side_extension;
stand_depth = case_depth + stand_depth_extension;
stand_slot_depth = case_depth + 2*stand_fit_clearance;
stand_slot_y = (stand_depth-stand_slot_depth)/2;
stand_case_bottom_z = stand_base_thickness + stand_under_case_clearance;

function box_contains_xy(p,b,r=0) =
    p[0]+r > b[0][0] && p[0]-r < b[0][0]+b[1][0] &&
    p[1]+r > b[0][1] && p[1]-r < b[0][1]+b[1][1];

module checks() {
    assert($preview || acknowledge_provisional_render || mechanical_interface_confirmed,
        "PROVISIONAL: F6/export requires acknowledge_provisional_render=true. Not fit-approved.");
    assert(!mechanical_interface_confirmed ||
        (antenna_review_confirmed && pcb_supports_confirmed && enable_pcb_supports &&
         len(pcb_holes)>=3 && len(antenna_keepout_boxes)>0),
        "Release needs actual antenna keepout and agreed PCB supports.");
    assert(wall>=1.6 && floor_thickness>=1.6 && lid_thickness>=1.6);
    assert(pcb_width>0 && pcb_height>0 && pcb_thickness>0);
    assert(pcb_support_height>component_height_bottom+0.5,
        "Insufficient rear-component clearance.");
    assert(pcb_origin[2]+pcb_thickness+component_height_top+1 < body_depth-lip_height,
        "Increase body_depth for the component envelope.");
    assert(corner_radius>wall && case_width>2*corner_radius && case_height>2*corner_radius);
    assert(lip_clearance>0 && lip_height>0 && lip_thickness>0);
    assert(usb_z-usb_opening_height/2>floor_thickness,
        "USB opening reaches floor.");
    assert(usb_z+usb_opening_height/2+usb_roof_rise<body_depth-2,
        "USB roof leaves too little material below lid.");
    assert(usb_x-usb_opening_width/2>wall+corner_radius &&
           usb_x+usb_opening_width/2<case_width-wall-corner_radius);
    assert(!enable_pcb_supports || ((pcb_supports_confirmed || prototype_supports_authorized) && len(pcb_holes)==3),
        "PCB supports need the three handoff holes and prototype or final authorization.");
    assert(pcb_support_clearance>fastener_thread_diameter && pcb_hole_drill>fastener_thread_diameter);
    assert(pcb_head_pocket_depth<floor_thickness && pcb_head_pocket_diameter<pcb_support_diameter);
    assert(pcb_screw_length>pcb_nut_bottom_z+fastener_nut_height+fastener_pitch);
    assert(pcb_screw_length<pcb_origin[2]+pcb_thickness+component_height_top);
    assert(fastener_washer_od<=pcb_support_diameter && fastener_nut_af/cos(30)<=pcb_support_diameter);
    assert(case_boss_diameter/2-case_nut_pocket_af/(2*cos(30))>=1.5);
    assert(case_nut_pocket_af>fastener_nut_af && case_nut_pocket_depth>fastener_nut_height);
    assert(usb_opening_width>=usb_plug_body_width_budget+2*usb_plug_clearance);
    assert(usb_opening_height>=usb_plug_body_height_budget+2*usb_plug_clearance);
    assert(!enable_sensor_baffle || thermal_baffle_confirmed,
        "Check PCB component/slot geometry before enabling baffle.");
    assert(sensor_vent_x>wall+lip_thickness+lip_clearance);
    assert(sensor_vent_x+sensor_vent_width<case_width-wall-lip_thickness-lip_clearance);
    assert(sensor_vent_y>sensor_bay_bottom_y+baffle_thickness);
    assert(sensor_vent_y+sensor_vent_length<sensor_bay_top_y-baffle_thickness);
    assert(sensor_bay_left_x+baffle_thickness<sensor_island_min[0]);
    assert(body_depth-sensor_case[2]>=sensor_minimum_free_air);
    assert(sensor_vent_y>stand_guide_height,"Shelf guide obstructs sensor side vents.");
    assert(stand_width-2*(stand_side_extension+stand_pedestal_width)>cable_tongue_width+2,
        "Shelf pedestals obstruct cable tongue.");
    assert(stand_under_case_clearance>cable_tongue_projection+3);
    for (b=antenna_keepout_boxes)
        assert(len(b)==2 && len(b[0])==3 && len(b[1])==3 &&
               b[1][0]>0 && b[1][1]>0 && b[1][2]>0,
               "Antenna box must contain a 3D origin and positive dimensions.");
    for (p=case_fastener_xy) {
        assert(p[0]>case_boss_diameter/2 && p[0]<case_width-case_boss_diameter/2);
        assert(p[1]>case_boss_diameter/2 && p[1]<case_height-case_boss_diameter/2);
        assert(p[0]+case_boss_diameter/2<pcb_origin[0] ||
               p[0]-case_boss_diameter/2>pcb_origin[0]+pcb_width,
               "Case boss collides with draft PCB outline.");
        assert(p[1]+case_boss_diameter/2<rf_reservation_min[1],
               "Case hardware extends above conservative full-case RF band boundary.");
        assert(p[1]+case_boss_diameter/2<sensor_bay_bottom_y ||
               p[1]-case_boss_diameter/2>sensor_bay_top_y,
               "Case boss crosses sensor vent/baffle region.");
        for (b=concat(antenna_keepout_boxes,rf_reservation_boxes))
            assert(!enable_case_fasteners || !box_contains_xy(p,b,case_boss_diameter/2),
                   "Case hardware enters antenna keepout in XY.");
    }
    for (p=wall_keyhole_xy) for (b=concat(antenna_keepout_boxes,rf_reservation_boxes))
        assert(!enable_wall_keyholes ||
               !box_contains_xy([p[0],p[1]+wall_keyhole_travel],b,wall_keyhole_entry_diameter/2),
               "Wall screw enters antenna keepout in XY.");
    for (p=pcb_holes) {
        assert(p[0]>=pcb_support_diameter/2 && p[0]<=pcb_width-pcb_support_diameter/2);
        assert(p[1]>=pcb_support_diameter/2 && p[1]<=pcb_height-pcb_support_diameter/2);
        for (b=concat(antenna_keepout_boxes,rf_reservation_boxes))
            assert(
                !box_contains_xy([p[0]+pcb_origin[0],p[1]+pcb_origin[1]],b,pcb_support_diameter/2));
        assert(!box_contains_xy([p[0]+pcb_origin[0],p[1]+pcb_origin[1]],
               [sensor_island_min,[sensor_island_max[0]-sensor_island_min[0],
                                   sensor_island_max[1]-sensor_island_min[1],1]],pcb_support_diameter/2),
               "Proposed PCB boss crosses sensor thermal island.");
    }
    if (!mechanical_interface_confirmed) echo("CONCEPT ONLY: board, USB, thermal and RF interfaces unverified.");
    if (len(antenna_keepout_boxes)==0) echo("ANTENNA KEEPOUT UNKNOWN: no RF clearance claim.");
    echo("A2 plug-body passage budget; actual cable mating unverified",[usb_plug_body_width_budget,usb_plug_body_height_budget],"face recess",usb_face_recess);
    echo(case_size_mm=[case_width,case_height,case_depth],pcb_A1_mm=[pcb_width,pcb_height,pcb_thickness]);
}

module rounded_rect(w,h,r) {
    hull() for (x=[r,w-r]) for (y=[r,h-r]) translate([x,y]) circle(r=r);
}
module shell_outline(h) {
    linear_extrude(height=h) rounded_rect(case_width,case_height,corner_radius);
}
module house_opening(w,h,depth) {
    // Cross section is X/Z after caller's rotation; 45-degree roof prints without a flat bridge.
    linear_extrude(height=depth)
        polygon([[-w/2,-h/2],[w/2,-h/2],[w/2,h/2],[0,h/2+w/2],[-w/2,h/2]]);
}
module usb_access_opening(depth) {
    linear_extrude(height=depth)
        polygon([[-usb_opening_width/2,-usb_opening_height/2],
                 [usb_opening_width/2,-usb_opening_height/2],
                 [usb_opening_width/2,usb_opening_height/2],
                 [usb_roof_flat_width/2,usb_opening_height/2+usb_roof_rise],
                 [-usb_roof_flat_width/2,usb_opening_height/2+usb_roof_rise],
                 [-usb_opening_width/2,usb_opening_height/2]]);
}
module hex_prism(af,h) { cylinder(d=af/cos(30),h=h,$fn=6); }
module keyhole_cut() {
    linear_extrude(height=floor_thickness+2*eps)
        union() {
            circle(d=wall_keyhole_entry_diameter);
            hull() { circle(d=wall_keyhole_neck);
                translate([0,wall_keyhole_travel]) circle(d=wall_keyhole_neck); }
        }
}
module case_bosses() {
    if(enable_case_fasteners) for(p=case_fastener_xy)
        translate([p[0],p[1],floor_thickness-eps])
            cylinder(d=case_boss_diameter,h=body_depth-floor_thickness+eps);
}
module pcb_supports() {
    if(enable_pcb_supports) for(p=pcb_holes)
        translate([pcb_origin[0]+p[0],pcb_origin[1]+p[1],floor_thickness-eps])
            cylinder(d=pcb_support_diameter,h=pcb_support_height+eps);
}
module base() {
    difference() {
        union() {
            difference() {
                shell_outline(body_depth);
                translate([wall,wall,floor_thickness])
                    linear_extrude(height=body_depth)
                        rounded_rect(case_width-2*wall,case_height-2*wall,corner_radius-wall);
            }
            case_bosses();
            pcb_supports();
            if(enable_cable_tongue)
                translate([usb_x-cable_tongue_width/2,-cable_tongue_projection,0])
                    cube([cable_tongue_width,cable_tongue_projection+wall+eps,floor_thickness]);
        }
        // Access tunnel reaches the receptacle face without moving the PCB.
        translate([usb_x,usb_mouth_case[1]+eps,usb_z]) rotate([90,0,0])
            usb_access_opening(usb_mouth_case[1]+2*eps);
        if(enable_pcb_supports) for(p=pcb_holes) {
            translate([pcb_origin[0]+p[0],pcb_origin[1]+p[1],-eps]) {
                cylinder(d=pcb_support_clearance,h=pcb_origin[2]+2*eps);
                // A conservative 1.6 mm recess accepts the head without forcing it proud.
                cylinder(d1=pcb_head_pocket_diameter,d2=pcb_support_clearance,h=pcb_head_pocket_depth+eps);
            }
        }
        // Right-side openings face the A0 sensor; no upper-left sensor bay remains.
        for(y=[sensor_vent_y:vent_pitch:sensor_vent_y+sensor_vent_length-vent_slot_width])
            translate([case_width-wall-eps,y+vent_slot_width/2,sensor_side_vent_z]) rotate([90,0,90])
                house_opening(vent_slot_width,8,wall+2*eps);
        // Separate left electronics air path, ending below the provisional RF band.
        for(y=[32:vent_pitch:39])
            translate([wall+eps,y+vent_slot_width/2,12]) rotate([90,0,-90])
                house_opening(vent_slot_width,8,wall+2*eps);
        if(enable_case_fasteners) for(p=case_fastener_xy) {
            translate([p[0],p[1],case_nut_bottom_z])
                hex_prism(case_nut_pocket_af,case_nut_pocket_depth+eps);
            // Load the nut laterally from the cavity; the roof retains it under screw load.
            translate([p[0]<case_width/2 ? p[0] : p[0]-case_boss_diameter/2-eps,
                       p[1]-case_nut_pocket_af/2,case_nut_bottom_z])
                cube([case_boss_diameter/2+eps,case_nut_pocket_af,case_nut_pocket_depth]);
            translate([p[0],p[1],body_depth-screw_relief_depth])
                cylinder(d=screw_relief_diameter,h=screw_relief_depth+eps);
        }
        if(enable_wall_keyholes) for(p=wall_keyhole_xy)
            translate([p[0],p[1],-eps]) keyhole_cut();
        if(enable_cable_tongue) for(dx=[-cable_tie_slot_spacing/2,cable_tie_slot_spacing/2])
            translate([usb_x+dx-cable_tie_slot_width/2,-cable_tongue_projection+3,-eps])
                cube([cable_tie_slot_width,cable_tie_slot_length,floor_thickness+2*eps]);
    }
}

module lid_lip() {
    inset=wall+lip_clearance;
    difference() {
        translate([inset,inset,-lip_height])
            linear_extrude(height=lip_height+eps)
                difference() {
                    rounded_rect(case_width-2*inset,case_height-2*inset,max(0.3,corner_radius-inset));
                    translate([lip_thickness,lip_thickness])
                        rounded_rect(case_width-2*(inset+lip_thickness),
                                     case_height-2*(inset+lip_thickness),0.4);
                }
        if(enable_case_fasteners) for(p=case_fastener_xy)
            translate([p[0],p[1],-lip_height-eps])
                cylinder(d=case_boss_diameter+2*lip_clearance,h=lip_height+3*eps);
    }
}
module sensor_baffle() {
    // Three lid-hung walls around the right sensor island; disabled pending layout/thermal review.
    z_bottom=pcb_origin[2]+pcb_thickness+baffle_pcb_gap-body_depth;
    x_end=case_width-wall-lip_clearance;
    translate([sensor_bay_left_x,sensor_bay_bottom_y,z_bottom])
        cube([baffle_thickness,sensor_bay_top_y-sensor_bay_bottom_y,-z_bottom+eps]);
    for(y=[sensor_bay_bottom_y,sensor_bay_top_y-baffle_thickness])
        translate([sensor_bay_left_x,y,z_bottom])
            cube([x_end-sensor_bay_left_x,baffle_thickness,-z_bottom+eps]);
}
module lid() {
    // Local Z=0 is the mating plane; negative Z is toward the board.
    difference() {
        union() { shell_outline(lid_thickness); lid_lip();
                  if(enable_sensor_baffle) sensor_baffle(); }
        if(enable_case_fasteners) for(p=case_fastener_xy)
            translate([p[0],p[1],-eps]) cylinder(d=lid_screw_clearance,h=lid_thickness+2*eps);
        for(x=[sensor_vent_x:vent_pitch:sensor_vent_x+sensor_vent_width-vent_slot_width])
            translate([x,sensor_vent_y,-eps])
                cube([vent_slot_width,sensor_vent_length,lid_thickness+2*eps]);
        // Left electronics intake, separated laterally from the right sensor island.
        for(x=[13:vent_pitch:23])
            translate([x,12,-eps]) cube([vent_slot_width,18,lid_thickness+2*eps]);
    }
}
module lid_print() {
    // Exterior face on bed, lip and optional baffle pointing upward.
    translate([0,case_height,lid_thickness]) rotate([180,0,0]) lid();
}
module stand() {
    // Two side saddles joined only by the bed plate. Center stays open for USB.
    difference() {
      union() {
        cube([stand_width,stand_depth,stand_base_thickness]);
        for(x=[stand_side_extension,stand_side_extension+case_width-stand_pedestal_width]) {
            translate([x,stand_slot_y-stand_rail_thickness,stand_base_thickness-eps])
                cube([stand_pedestal_width,stand_slot_depth+2*stand_rail_thickness,
                      stand_under_case_clearance+eps]);
            for(y=[stand_slot_y-stand_rail_thickness,stand_slot_y+stand_slot_depth])
                translate([x,y,stand_case_bottom_z-eps])
                    cube([stand_pedestal_width,stand_rail_thickness,stand_guide_height+eps]);
        }
        // Outside stops resist sideways sliding; no snap arms to fatigue.
        for(x=[stand_side_extension-stand_rail_thickness-stand_fit_clearance,
               stand_side_extension+case_width+stand_fit_clearance])
            translate([x,stand_slot_y-stand_rail_thickness,stand_base_thickness-eps])
                cube([stand_rail_thickness,stand_slot_depth+2*stand_rail_thickness,
                      stand_under_case_clearance+stand_guide_height+eps]);
      }
      // Bottom lid screw heads/6 mm washers would otherwise meet the front guides.
      for(x=[stand_side_extension+case_boss_x_from_edge,
             stand_side_extension+case_width-case_boss_x_from_edge])
        translate([x,stand_slot_y+eps,stand_case_bottom_z+case_screw_bottom_y]) rotate([90,0,0])
            cylinder(d=stand_screw_relief_diameter,h=stand_rail_thickness+2*eps);
    }
}
module wall_spacer() {
    difference() { cylinder(d=wall_spacer_diameter,h=wall_spacer_height);
        translate([0,0,-eps]) cylinder(d=wall_keyhole_neck+0.6,h=wall_spacer_height+2*eps); }
}
module coupon() {
    // Prototype M2.5 nut pocket AF sweep 5.0..5.4 plus PCB head/bore coupon.
    $fn=40; // avoid near-collinear CGAL triangulation slivers on this flat multi-hole coupon
    difference() {
        cube([52,14,8]);
        for(i=[0:4]) translate([6+i*10,7,8-case_nut_pocket_depth])
            hex_prism(case_nut_pocket_af+(i-2)*0.1,case_nut_pocket_depth+eps);
        for(i=[0:4]) translate([6+i*10,7,-eps]) {
            cylinder(d=pcb_support_clearance,h=8+2*eps);
            cylinder(d1=pcb_head_pocket_diameter,d2=pcb_support_clearance,h=pcb_head_pocket_depth+eps);
        }
    }
}
module washer() {
    difference(){cylinder(d=fastener_washer_od,h=fastener_washer_thickness);
        translate([0,0,-eps])cylinder(d=fastener_washer_id,h=fastener_washer_thickness+2*eps);}
}
module nut() {
    difference(){hex_prism(fastener_nut_af,fastener_nut_height);
        translate([0,0,-eps])cylinder(d=fastener_thread_diameter,h=fastener_nut_height+2*eps);}
}
module pcb_hardware() {
    for(p=pcb_holes) translate([pcb_origin[0]+p[0],pcb_origin[1]+p[1],0]) {
        // Conservative nominal hardware envelopes; threads and drive recesses omitted.
        cylinder(d=pcb_head_diameter,h=0.4);
        translate([0,0,0.4])cylinder(d1=pcb_head_diameter,d2=fastener_thread_diameter,h=pcb_head_height-0.4);
        cylinder(d=fastener_thread_diameter,h=pcb_screw_length);
        translate([0,0,pcb_origin[2]+pcb_thickness])washer();
        translate([0,0,pcb_nut_bottom_z])nut();
    }
}
module case_hardware() {
    for(p=case_fastener_xy) translate([p[0],p[1],0]) {
        translate([0,0,case_nut_seated_z])nut();
        translate([0,0,case_depth])washer();
        translate([0,0,case_depth+fastener_washer_thickness-case_screw_length])
            cylinder(d=fastener_thread_diameter,h=case_screw_length);
        translate([0,0,case_depth+fastener_washer_thickness])
            cylinder(d=case_head_diameter,h=case_head_height);
    }
}
module usb_plug_body_sweep(clearance=0) {
    // Swept to the front face (more conservative than the 1.85 mm mating-body gap).
    translate([usb_x-usb_plug_body_width_budget/2-clearance,-cable_tongue_projection-20,
               usb_z-usb_plug_body_height_budget/2-clearance])
        cube([usb_plug_body_width_budget+2*clearance,
              usb_mouth_case[1]+cable_tongue_projection+20,
              usb_plug_body_height_budget+2*clearance]);
}
module usb_plug_insertion_sweep(clearance=0) {
    // Mated shoulder honors GCT's 1.85 mm minimum gap, with an 8 mm removal stroke.
    y_end=usb_mouth_case[1]-usb_mated_body_gap;
    translate([usb_x-usb_plug_body_width_budget/2-clearance,
               y_end-usb_plug_body_length_budget-usb_insertion_travel_budget-clearance,
               usb_z-usb_plug_body_height_budget/2-clearance])
        cube([usb_plug_body_width_budget+2*clearance,
              usb_plug_body_length_budget+usb_insertion_travel_budget+2*clearance,
              usb_plug_body_height_budget+2*clearance]);
}
module reference_geometry() {
    // Background-only geometry: never appears in STL exports.
    if(show_reference_board) %color([0.1,0.6,0.4,0.5])
        translate(pcb_origin) cube([pcb_width,pcb_height,pcb_thickness]);
    if(show_reference_board) {
        %color([0.3,0.4,0.6,0.65]) translate(module_case_origin) cube(module_size);
        %color([0.1,0.65,0.8,0.8]) translate([sensor_case[0]-sensor_body_width/2,
            sensor_case[1]-sensor_body_width/2,pcb_origin[2]+pcb_thickness])
            cube([sensor_body_width,sensor_body_width,sensor_body_height]);
        %color([0.55,0.55,0.55,0.6]) translate([usb_x-usb_shell_width/2,usb_mouth_case[1],
            pcb_origin[2]+pcb_thickness]) cube([usb_shell_width,usb_shell_depth,usb_shell_height]);
        if(!enable_pcb_supports) for(p=pcb_holes) %color([0.15,0.35,0.8,0.45])
            translate([pcb_origin[0]+p[0],pcb_origin[1]+p[1],floor_thickness])
                cylinder(d=pcb_support_diameter,h=pcb_support_height);
    }
    if(show_keepouts) {
        for(b=rf_reservation_boxes) %color([0.95,0.5,0.05,0.2]) translate(b[0]) cube(b[1]);
        %color([0.2,0.8,0.9,0.25]) translate([sensor_case[0]-sensor_body_width/2,
            sensor_case[1]-sensor_body_width/2,sensor_case[2]])
                cube([sensor_body_width,sensor_body_width,sensor_minimum_free_air]);
    }
    if(show_keepouts) for(b=antenna_keepout_boxes)
        %color([0.95,0.15,0.25,0.3]) translate(b[0]) cube(b[1]);
    if(show_hardware) {
        %color([0.65,0.67,0.7,0.85])pcb_hardware();
        %color([0.65,0.67,0.7,0.85])case_hardware();
    }
}
module assembly(gap=0) {
    color([0.72,0.76,0.8]) base();
    color([0.91,0.92,0.93]) translate([0,0,body_depth+gap]) lid();
    reference_geometry();
}

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
