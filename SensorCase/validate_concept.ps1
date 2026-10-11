param()
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$root = $PSScriptRoot
$sourcePath = Join-Path $root 'sensor_enclosure.scad'
$source = Get-Content -LiteralPath $sourcePath -Raw
$interface = Get-Content -LiteralPath (Join-Path $root 'mechanical_interface.json') -Raw | ConvertFrom-Json
$pcb = Get-Content -LiteralPath (Join-Path $root 'pcb_A1_mechanical_interface.json') -Raw | ConvertFrom-Json
$checks = [System.Collections.Generic.List[object]]::new()
function Check([string]$Name, [bool]$Passed, $Evidence) {
    $checks.Add([pscustomobject][ordered]@{name=$Name; passed=$Passed; evidence=$Evidence})
}
function Num([string]$Name) {
    $m = [regex]::Match($source, '(?m)^' + [regex]::Escape($Name) + '\s*=\s*(-?\d+(?:\.\d+)?)\s*;')
    if (!$m.Success) { throw "Expected literal numeric parameter: $Name" }
    [double]::Parse($m.Groups[1].Value, [Globalization.CultureInfo]::InvariantCulture)
}
function Fmt([double]$Value) { $Value.ToString('0.###', [Globalization.CultureInfo]::InvariantCulture) }
function Arr([string]$Name) {
    $m=[regex]::Match($source,'(?m)^'+[regex]::Escape($Name)+'\s*=\s*(\[[^;]*\])\s*;')
    if(!$m.Success){throw "Expected literal numeric array: $Name"}
    return ,(ConvertFrom-Json $m.Groups[1].Value -NoEnumerate)
}
function Same($A,$B) {
    if($A -is [Array] -and $B -is [Array]) {
        if($A.Count -ne $B.Count){return $false}
        for($k=0;$k -lt $A.Count;$k++){if(!(Same $A[$k] $B[$k])){return $false}}
        return $true
    }
    return [math]::Abs([double]$A-[double]$B) -lt 0.00001
}
function Near([double]$A,[double]$B) { return [math]::Abs($A-$B) -lt 0.00001 }
function Hits($P,$Min,$Max,[double]$Radius) {
    return $P[0]+$Radius -gt $Min[0] -and $P[0]-$Radius -lt $Max[0] -and $P[1]+$Radius -gt $Min[1] -and $P[1]-$Radius -lt $Max[1]
}

# Delimiter scan is intentionally not described as a CAD syntax check.
$stripped = [regex]::Replace($source, '/\*[\s\S]*?\*/|//[^\r\n]*|"(?:\\.|[^"\\])*"', '')
$stack = [System.Collections.Generic.Stack[char]]::new()
$pairs = @{')'='(';']'='[';'}'='{'}
$balanced = $true
foreach ($char in $stripped.ToCharArray()) {
    if ('([{'.Contains([string]$char)) { $stack.Push($char) }
    elseif (')]}'.Contains([string]$char)) {
        if ($stack.Count -eq 0 -or $stack.Pop() -ne $pairs[[string]$char]) { $balanced=$false; break }
    }
}
Check 'Source delimiters balance after removing strings/comments' ($balanced -and $stack.Count -eq 0) 'Not a parser or render test'
Check 'Interface is explicitly provisional' ($interface.status -eq 'PROVISIONAL_CONCEPT_NOT_FIT_APPROVED') $interface.status
Check 'PCB A1 hole proposals use explicit upper-left-to-lower-left transform' ($source -match 'pcb_holes = \[for\(p=pcb_holes_top_view\) pcb_top_to_local\(p\)\]' -and $source -match 'function pcb_top_to_local\(p\) = \[p\[0\],pcb_height-p\[1\]\]') 'Prototype supports use unchanged handoff holes'
foreach ($gate in @('mechanical_interface_confirmed','acknowledge_provisional_render','antenna_review_confirmed','pcb_supports_confirmed','thermal_baffle_confirmed','enable_sensor_baffle')) {
    Check "$gate remains false" ($source -match ('(?m)^'+$gate+'\s*=\s*false\s*;')) 'Provisional gate preserved'
}
Check 'Prototype PCB supports explicitly enabled without final approval' ($source -match '(?m)^enable_pcb_supports\s*=\s*true;' -and $source -match '(?m)^prototype_supports_authorized\s*=\s*true;') 'Prototype only'
Check 'Antenna keepout remains explicitly unknown' ($source -match '(?m)^antenna_keepout_boxes\s*=\s*\[\s*\]\s*;') 'Empty means unknown, not a clearance approval'

$wall=Num 'wall'; $floor=Num 'floor_thickness'; $lid=Num 'lid_thickness'
$body=Num 'body_depth'; $pw=Num 'pcb_width'; $ph=Num 'pcb_height'; $pt=Num 'pcb_thickness'
$w=$pw+2*(Num 'side_margin')+2*$wall
$h=$ph+(Num 'bottom_margin')+(Num 'top_margin')+2*$wall
$depth=$body+$lid
$px=$wall+(Num 'side_margin'); $py=$wall+(Num 'bottom_margin'); $pz=$floor+(Num 'pcb_support_height')
$usb=Arr 'usb_mouth_top_view'; $ux=$px+$usb[0]; $uy=$py+$ph-$usb[1]; $uz=$pz+$pt+(Num 'usb_center_above_pcb_top')
$uw=Num 'usb_opening_width'; $uh=Num 'usb_opening_height'
$bossR=(Num 'case_boss_diameter')/2; $bossX=Num 'case_boss_x_from_edge'
$nutCorner=(Num 'case_nut_pocket_af')/[math]::Cos([math]::PI/6)
$topGap=$body-(Num 'lip_height')-($pz+$pt+(Num 'component_height_top'))
$rearGap=(Num 'pcb_support_height')-(Num 'component_height_bottom')
$usbRoof=$body-($uz+$uh/2+($uw-(Num 'usb_roof_flat_width'))/2)
$bossBoardGap=$px-($bossX+$bossR)
$standW=$w+2*(Num 'stand_side_extension')
$standD=$depth+(Num 'stand_depth_extension')
$standH=(Num 'stand_base_thickness')+(Num 'stand_under_case_clearance')+(Num 'stand_guide_height')
$shelfBottom=(Num 'stand_base_thickness')+(Num 'stand_under_case_clearance')
$shelfHeight=$h+$shelfBottom
Check 'Shell dimensions agree with interface' ((Near $w $interface.packaging_provisional.case_body_and_lid[0]) -and (Near $h $interface.packaging_provisional.case_body_and_lid[1]) -and (Near $depth $interface.packaging_provisional.case_body_and_lid[2])) @($w,$h,$depth)
Check 'Shell wall/floor/lid at least 1.6 mm' ($wall -ge 1.6 -and $floor -ge 1.6 -and $lid -ge 1.6) @($wall,$floor,$lid)
Check 'Rear component envelope has clearance' ($rearGap -gt 0.5) ([ordered]@{clearance_mm=$rearGap})
Check 'Front component envelope clears lip bottom plane' ($topGap -gt 1) ([ordered]@{clearance_mm=$topGap})
Check 'USB peak leaves more than 2 mm below lid' ($usbRoof -gt 2) ([ordered]@{remaining_mm=$usbRoof})
Check 'USB opening clears floor' ($uz-$uh/2 -gt $floor) ([ordered]@{remaining_mm=$uz-$uh/2-$floor})
Check 'Case bosses clear PCB A1 in X' ($bossBoardGap -gt 0) ([ordered]@{gap_mm=$bossBoardGap})
Check 'Captive-nut pocket leaves at least 1.5 mm radial boss material' ($bossR-$nutCorner/2 -ge 1.5) ([ordered]@{radial_mm=$bossR-$nutCorner/2})
Check 'Bosses overlap sidewall for connected solid' ($bossX-$bossR -lt $wall) ([ordered]@{overlap_mm=$wall-($bossX-$bossR)})
Check 'Stand center clears cable tongue' ($w-2*(Num 'stand_pedestal_width') -gt (Num 'cable_tongue_width')+2) ([ordered]@{center_width_mm=$w-2*(Num 'stand_pedestal_width')})
Check 'Stand provides space below tongue' ((Num 'stand_under_case_clearance') -gt (Num 'cable_tongue_projection')+3) ([ordered]@{remaining_mm=(Num 'stand_under_case_clearance')-(Num 'cable_tongue_projection')})
Check 'Stand dimensions agree with interface' ((Near $standW $interface.packaging_provisional.shelf_cradle_envelope[0]) -and (Near $standD $interface.packaging_provisional.shelf_cradle_envelope[1]) -and (Near $standH $interface.packaging_provisional.shelf_cradle_envelope[2])) @($standW,$standD,$standH)
Check 'Shelf assembly height agrees with interface' (Near $shelfHeight $interface.packaging_provisional.shelf_assembled_height) $shelfHeight
$sensor=Arr 'sensor_top_view'; $sensorX=$px+$sensor[0]; $sensorY=$py+$ph-$sensor[1]; $sensorZ=$pz+$pt+(Num 'sensor_body_height')
$island=Arr 'sensor_island_top_view'; $islandMin=@(($px+$island[0][0]),($py+$ph-$island[1][1])); $islandMax=@(($px+$island[1][0]),($py+$ph-$island[0][1]))
Check 'Current routed A1 slot metadata received' ($pcb.revision -eq 'A1-routed-provisional' -and $pcb.sensor_slot_proposal.implemented_as_edge_cuts -eq $true -and $interface.pcb_features_provisional.thermal_slots_routed -eq $true) $pcb.revision
$slotEnvelopeFits=$true
foreach($path in @($pcb.sensor_slot_proposal.top_centerline,$pcb.sensor_slot_proposal.bottom_centerline)) {
    foreach($point in $path) {
        $r=$pcb.sensor_slot_proposal.width/2
        if($point[0]-$r -lt $island[0][0] -or $point[0]+$r -gt $island[1][0] -or $point[1]-$r -lt $island[0][1] -or $point[1]+$r -gt $island[1][1]){$slotEnvelopeFits=$false}
    }
}
Check 'Both implemented L-slot swept bounds fit inside reserved island' $slotEnvelopeFits 'Includes 0.5 mm cap radius; no support or baffle allowed in the full reservation'
$ventX=$sensorX-(Num 'vent_slot_width')/2; $ventY=$sensorY-(Num 'sensor_vent_length')/2
$baffleLeft=$islandMin[0]-(Num 'sensor_baffle_island_gap')-(Num 'baffle_thickness')
$baffleBottom=$islandMin[1]-(Num 'sensor_baffle_island_gap')-(Num 'baffle_thickness')
$baffleTop=$islandMax[1]+(Num 'sensor_baffle_island_gap')+(Num 'baffle_thickness')
$rf=Arr 'rf_reservation_top_view'; $rfMin=@(($px+$rf[0][0]),($py+$ph-$rf[1][1])); $rfMax=@(($px+$rf[1][0]),($py+$ph-$rf[0][1]))
$holes=Arr 'pcb_holes_top_view'; $holesLocal=@(); $holesCase=@()
foreach($hole in $holes){ $holesLocal+=,@($hole[0],($ph-$hole[1])); $holesCase+=,@(($px+$hole[0]),($py+$ph-$hole[1])) }
Check 'PCB dimensions match sibling A1 snapshot' ((Near $pw $pcb.board.width) -and (Near $ph $pcb.board.height) -and (Near $pt $pcb.board.thickness)) @($pw,$ph,$pt)
$expectedHoles=@($pcb.holes | ForEach-Object { ,@($_.x,$_.y) })
Check 'Hole coordinates match sibling A1 snapshot' (Same $holes $expectedHoles) $holes
Check 'Transformed holes match interface' (Same $holesLocal $interface.pcb_features_provisional.holes_local) $holesLocal
$holesMatch=$true; for($i=0;$i -lt $holesCase.Count;$i++){for($j=0;$j -lt 2;$j++){if(!(Near $holesCase[$i][$j] $interface.pcb_features_provisional.holes_case[$i][$j])){$holesMatch=$false}}}
Check 'Case-coordinate hole centers match interface' $holesMatch $holesCase
Check 'Hole and boss diameters match PCB proposal' ((Near (Num 'pcb_hole_drill') $pcb.holes[0].drill) -and (Near (Num 'pcb_support_diameter') $pcb.boss_reserved_diameter)) @((Num 'pcb_hole_drill'),(Num 'pcb_support_diameter'))
Check 'USB mouth and axis match sibling' ((Near $usb[0] $pcb.usb.mouth_center_x) -and (Near $usb[1] $pcb.usb.mouth_y) -and (Near (Num 'usb_center_above_pcb_top') $pcb.usb.mating_center_z)) @($ux,$uy,$uz)
Check 'USB shell nominal dimensions match sibling' ((Near (Num 'usb_shell_width') $pcb.usb.shell_width) -and (Near (Num 'usb_shell_depth') $pcb.usb.body_length) -and (Near (Num 'usb_shell_height') $pcb.usb.height_above_board)) 'GCT USB4105-GF-A'
Check 'USB setback retained with documented body-access strategy' ((Near $uy 4.4) -and $interface.remaining_inputs.usb_insertion_check -match '18 x 10') @{recess_mm=$uy;actual_cable_fit_verified=$false}
Check 'USB aperture clears body-budget sweep with margin' ($uw -ge (Num 'usb_plug_body_width_budget')+2*(Num 'usb_plug_clearance') -and $uh -ge (Num 'usb_plug_body_height_budget')+2*(Num 'usb_plug_clearance')) @{aperture=@($uw,$uh);body_budget=@((Num 'usb_plug_body_width_budget'),(Num 'usb_plug_body_height_budget'));sweep_margin=(Num 'usb_plug_clearance')}
$plugSweepBottom=$shelfBottom+$uy-(Num 'usb_mated_body_gap')-(Num 'usb_plug_body_length_budget')-(Num 'usb_insertion_travel_budget')-(Num 'usb_plug_clearance')
Check 'Defined plug insertion sweep clears shelf bed plate' ($plugSweepBottom -gt (Num 'stand_base_thickness')) @{clearance_mm=$plugSweepBottom-(Num 'stand_base_thickness');actual_cable_bend_verified=$false}
Check 'PCB through-bolt clears printed bore and board NPTH' ((Num 'fastener_thread_diameter') -lt (Num 'pcb_support_clearance') -and (Num 'fastener_thread_diameter') -lt (Num 'pcb_hole_drill')) 'M2.5 shank in 2.9 printed bore and 2.7 PCB hole'
Check 'PCB screw head recess stays within floor and boss diameter' ((Num 'pcb_head_pocket_depth') -lt $floor -and (Num 'pcb_head_pocket_diameter') -lt (Num 'pcb_support_diameter')) @{remaining_floor_mm=$floor-(Num 'pcb_head_pocket_depth')}
$pcbNutTop=$pz+$pt+(Num 'fastener_washer_thickness')+(Num 'fastener_nut_height')
Check 'PCB screw engages nut with exposed thread and stays below component reserve' ((Num 'pcb_screw_length') -gt $pcbNutTop+(Num 'fastener_pitch') -and (Num 'pcb_screw_length') -lt $pz+$pt+(Num 'component_height_top')) @{thread_beyond_nut_mm=(Num 'pcb_screw_length')-$pcbNutTop}
Check 'PCB washer and nut fit in 6 mm reserved mounting envelope' ((Num 'fastener_washer_od') -le (Num 'pcb_support_diameter') -and (Num 'fastener_nut_af')/[math]::Cos([math]::PI/6) -le (Num 'pcb_support_diameter')) 'No PCB hole or island relocation'
$caseNutBottom=$body-(Num 'case_nut_roof')-(Num 'fastener_nut_height')
$caseScrewTip=$depth+(Num 'fastener_washer_thickness')-(Num 'case_screw_length')
Check 'Case screw engages captive nut without bottoming' ($caseScrewTip -lt $caseNutBottom-(Num 'fastener_pitch') -and $caseScrewTip -gt $body-(Num 'screw_relief_depth')) @{thread_beyond_nut_mm=$caseNutBottom-$caseScrewTip;bottom_clearance_mm=$caseScrewTip-($body-(Num 'screw_relief_depth'))}
Check 'Case nut has retaining roof and lateral loading slot' ((Num 'case_nut_roof') -ge 2 -and $source -match 'Load the nut laterally') 'Top-drop unretained nut is not used'
Check 'Stand guide relief covers lower screw/washer envelope' ((Num 'stand_screw_relief_diameter') -ge (Num 'fastener_washer_od')+1) @{diameter=(Num 'stand_screw_relief_diameter')}
Check 'SHT40 position matches sibling' ((Near $sensor[0] $pcb.sensor.x) -and (Near $sensor[1] $pcb.sensor.y) -and (Near (Num 'sensor_body_height') $pcb.sensor.body_height)) @($sensorX,$sensorY,$sensorZ)
Check 'At least 2 mm unobstructed column above sensor body to lid' ($body-$sensorZ -ge $pcb.sensor.minimum_free_air_above) @{available_mm=$body-$sensorZ;required_mm=$pcb.sensor.minimum_free_air_above}
Check 'Optional baffle stays outside entire sensor island/slot region' ($baffleLeft+(Num 'baffle_thickness') -lt $islandMin[0] -and $baffleBottom+(Num 'baffle_thickness') -lt $islandMin[1] -and $baffleTop-(Num 'baffle_thickness') -gt $islandMax[1]) @{island_min=$islandMin;island_max=$islandMax}
Check 'Front vents fit inside baffle bay and align with sensor' ($ventY -gt $baffleBottom+(Num 'baffle_thickness') -and $ventY+(Num 'sensor_vent_length') -lt $baffleTop-(Num 'baffle_thickness') -and $ventX -gt $baffleLeft+(Num 'baffle_thickness') -and $ventX+(Num 'sensor_vent_width') -lt $w-$wall-(Num 'lip_clearance')-(Num 'lip_thickness')) @($ventX,$ventY)
Check 'Shelf side guide ends below sensor vents' ($ventY -gt (Num 'stand_guide_height')) @{gap_mm=$ventY-(Num 'stand_guide_height')}
Check 'RF band follows sibling 12 mm reservation' ((Near $rf[0][0] $pcb.rf_mechanical_reserve.x0) -and (Near $rf[0][1] $pcb.rf_mechanical_reserve.y0) -and (Near $rf[1][0] $pcb.rf_mechanical_reserve.x1) -and (Near $rf[1][1] $pcb.rf_mechanical_reserve.y1)) @{case_min=$rfMin;case_max=$rfMax;manufacturer_3d_rule=$false}
Check 'PCB-only copper keepout stays separate from mechanical reserve' ((Near (Num 'pcb_copper_keepout_depth') $pcb.rf_pcb_copper_keepout.y1) -and (Num 'pcb_copper_keepout_depth') -lt $rf[1][1]) '3.3 mm PCB copper rule is not a plastic clearance rule'
$hardwareMinRF=[double]::PositiveInfinity; $islandClear=$true; $holeEdgeClear=$true
foreach($p in $holesCase){$hardwareMinRF=[math]::Min($hardwareMinRF,$rfMin[1]-$p[1]-(Num 'pcb_support_diameter')/2); if(Hits $p $islandMin $islandMax ((Num 'pcb_support_diameter')/2)){$islandClear=$false}}
foreach($p in $holesLocal){$r=(Num 'pcb_support_diameter')/2;if($p[0]-$r -lt 0 -or $p[0]+$r -gt $pw -or $p[1]-$r -lt 0 -or $p[1]+$r -gt $ph){$holeEdgeClear=$false}}
Check 'Proposed PCB bosses avoid sensor island and thermal slots' $islandClear 'Boss radius 3 mm; lower-right boss ends 1 mm below reserved island'
Check 'Proposed PCB bosses fit within board edges' $holeEdgeClear '6 mm reserved diameter'
Check 'Proposed PCB bosses stay below RF reservation' ($hardwareMinRF -gt 0) @{minimum_y_gap_mm=$hardwareMinRF}
$caseTop=$h-(Num 'case_screw_top_offset'); $caseBottom=Num 'case_screw_bottom_y'
Check 'Entire case bosses stay below RF band across full case width' ($caseTop+$bossR -lt $rfMin[1]) @{gap_mm=$rfMin[1]-$caseTop-$bossR}
Check 'Case bosses avoid sensor bay and side vents' ($caseBottom+$bossR -lt $baffleBottom -and $caseTop-$bossR -gt $baffleTop) 'Lower case screws moved to Y=6; upper screws at Y=41.8'
Check 'Wall screw envelope stays below RF band' ((Num 'wall_keyhole_entry_y')+(Num 'wall_keyhole_travel')+(Num 'wall_keyhole_entry_diameter')/2 -lt $rfMin[1]) 'Provisional screw-head envelope; real hardware pending'
$mod=Arr 'module_top_view_origin';$modSize=Arr 'module_size'
Check 'Module envelope matches sibling' ((Near $mod[0] $pcb.module.body_x) -and (Near $mod[1] $pcb.module.body_y) -and (Near $modSize[0] $pcb.module.width) -and (Near $modSize[1] $pcb.module.length) -and (Near $modSize[2] $pcb.module.height)) $pcb.module.part
$exports=@(Get-ChildItem -LiteralPath $root -File | Where-Object {$_.Extension -in @('.stl','.3mf','.step','.stp')})
Check 'No unlabelled mesh or STEP at workspace root' ($exports.Count -eq 0) ([ordered]@{export_count=$exports.Count;note='Approved concept outputs belong under provisional_cad with a separate CAD report'})

# One drawing API writes both SVG and PNG: this is a source-derived schematic.
Add-Type -AssemblyName System.Drawing
$bitmap=[Drawing.Bitmap]::new(1500,960)
$graphics=[Drawing.Graphics]::FromImage($bitmap)
$graphics.SmoothingMode=[Drawing.Drawing2D.SmoothingMode]::AntiAlias
$graphics.Clear([Drawing.ColorTranslator]::FromHtml('#f6f7f9'))
$svg=[System.Text.StringBuilder]::new()
[void]$svg.AppendLine('<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="960" viewBox="0 0 1500 960">')
[void]$svg.AppendLine('<rect width="1500" height="960" fill="#f6f7f9"/>')
function Rect([double]$X,[double]$Y,[double]$W,[double]$H,[string]$Fill,[string]$Stroke='#253348',[double]$StrokeW=1,[bool]$Dash=$false) {
    if($Fill -ne 'none') { $brush=[Drawing.SolidBrush]::new([Drawing.ColorTranslator]::FromHtml($Fill)); $graphics.FillRectangle($brush,[single]$X,[single]$Y,[single]$W,[single]$H); $brush.Dispose() }
    if($Stroke -ne 'none') { $pen=[Drawing.Pen]::new([Drawing.ColorTranslator]::FromHtml($Stroke),[single]$StrokeW); if($Dash){$pen.DashStyle=[Drawing.Drawing2D.DashStyle]::Dash}; $graphics.DrawRectangle($pen,[single]$X,[single]$Y,[single]$W,[single]$H); $pen.Dispose() }
    $dashAttr=if($Dash){' stroke-dasharray="6 5"'}else{''}
    [void]$svg.AppendLine('<rect x="'+(Fmt $X)+'" y="'+(Fmt $Y)+'" width="'+(Fmt $W)+'" height="'+(Fmt $H)+'" fill="'+$Fill+'" stroke="'+$Stroke+'" stroke-width="'+(Fmt $StrokeW)+'"'+$dashAttr+'/>')
}
function Line([double]$X1,[double]$Y1,[double]$X2,[double]$Y2,[string]$Color='#506177',[double]$Width=1,[bool]$Dash=$false) {
    $pen=[Drawing.Pen]::new([Drawing.ColorTranslator]::FromHtml($Color),[single]$Width); if($Dash){$pen.DashStyle=[Drawing.Drawing2D.DashStyle]::Dash}; $graphics.DrawLine($pen,[single]$X1,[single]$Y1,[single]$X2,[single]$Y2); $pen.Dispose()
    $dashAttr=if($Dash){' stroke-dasharray="6 5"'}else{''}
    [void]$svg.AppendLine('<line x1="'+(Fmt $X1)+'" y1="'+(Fmt $Y1)+'" x2="'+(Fmt $X2)+'" y2="'+(Fmt $Y2)+'" stroke="'+$Color+'" stroke-width="'+(Fmt $Width)+'"'+$dashAttr+'/>')
}
function Circle([double]$X,[double]$Y,[double]$R,[string]$Fill,[string]$Stroke='#253348') {
    $brush=[Drawing.SolidBrush]::new([Drawing.ColorTranslator]::FromHtml($Fill)); $pen=[Drawing.Pen]::new([Drawing.ColorTranslator]::FromHtml($Stroke),1)
    $graphics.FillEllipse($brush,[single]($X-$R),[single]($Y-$R),[single](2*$R),[single](2*$R)); $graphics.DrawEllipse($pen,[single]($X-$R),[single]($Y-$R),[single](2*$R),[single](2*$R)); $brush.Dispose();$pen.Dispose()
    [void]$svg.AppendLine('<circle cx="'+(Fmt $X)+'" cy="'+(Fmt $Y)+'" r="'+(Fmt $R)+'" fill="'+$Fill+'" stroke="'+$Stroke+'"/>')
}
function Label([double]$X,[double]$Y,[string]$Value,[int]$Size=17,[string]$Color='#253348',[bool]$Bold=$false) {
    $style=if($Bold){[Drawing.FontStyle]::Bold}else{[Drawing.FontStyle]::Regular}
    $font=[Drawing.Font]::new('Arial',[single]$Size,$style,[Drawing.GraphicsUnit]::Pixel); $brush=[Drawing.SolidBrush]::new([Drawing.ColorTranslator]::FromHtml($Color))
    $graphics.DrawString($Value,$font,$brush,[single]$X,[single]$Y);$font.Dispose();$brush.Dispose()
    $weight=if($Bold){'700'}else{'400'}; $escaped=[Security.SecurityElement]::Escape($Value)
    [void]$svg.AppendLine('<text x="'+(Fmt $X)+'" y="'+(Fmt ($Y+$Size))+'" font-family="Arial,sans-serif" font-size="'+$Size+'" font-weight="'+$weight+'" fill="'+$Color+'">'+$escaped+'</text>')
}

Label 42 24 'ROOM SENSOR / PROTOTYPE A2 - PCB A1' 30 '#192b40' $true
Label 42 66 'PROVISIONAL DIMENSIONS  |  Source-derived schematic, not a CAD render or fabrication drawing' 18 '#a55c00' $true
Label 70 112 'FRONT / INTERIOR OVERLAY' 17 '#52667c' $true
Label 1030 112 'SIDE SECTION / SHELF' 17 '#52667c' $true
$scale=6.0; $fx=70.0; $fy=174.0; $bottom=$fy+$h*$scale; $right=$fx+$w*$scale
Rect $fx $fy ($w*$scale) ($h*$scale) '#e1e6ec' '#253348' 2
Rect ($fx+$wall*$scale) ($fy+$wall*$scale) (($w-2*$wall)*$scale) (($h-2*$wall)*$scale) '#ffffff' '#98a6b6'
Rect ($fx+$px*$scale) ($fy+($h-$py-$ph)*$scale) ($pw*$scale) ($ph*$scale) '#e7f2ed' '#569880' 1.5 $true
Label ($fx+$px*$scale+12) ($fy+($h-$py-$ph)*$scale+120) 'PCB A1 draft' 18 '#35745c' $true
Label ($fx+$px*$scale+12) ($fy+($h-$py-$ph)*$scale+146) ((Fmt $pw)+' x '+(Fmt $ph)+' mm') 17 '#35745c'
Rect ($fx+$rfMin[0]*$scale) ($fy+($h-$rfMax[1])*$scale) (($rfMax[0]-$rfMin[0])*$scale) (($rfMax[1]-$rfMin[1])*$scale) '#fde5c7' '#c27c27' 1 $true
Label ($fx+$rfMin[0]*$scale+5) ($fy+($h-$rfMax[1])*$scale-22) '12 mm RF reservation' 15 '#916425' $true
Rect ($fx+($px+$mod[0])*$scale) ($fy+($h-$py-$ph+$mod[1])*$scale) ($modSize[0]*$scale) ($modSize[1]*$scale) '#b7c4da' '#556889'
Rect ($fx+$islandMin[0]*$scale) ($fy+($h-$islandMax[1])*$scale) (($islandMax[0]-$islandMin[0])*$scale) (($islandMax[1]-$islandMin[1])*$scale) '#e8dced' '#9561a0' 1 $true
foreach($p in $holesCase) { Circle ($fx+$p[0]*$scale) ($fy+($h-$p[1])*$scale) ((Num 'pcb_hole_drill')*$scale/2) '#ffffff' '#306cba' }
for($x=$ventX;$x -le $ventX+(Num 'sensor_vent_width')-(Num 'vent_slot_width')+0.0001;$x+=(Num 'vent_pitch')) {
    Rect ($fx+$x*$scale) ($fy+($h-$ventY-(Num 'sensor_vent_length'))*$scale) ((Num 'vent_slot_width')*$scale) ((Num 'sensor_vent_length')*$scale) '#498d96' 'none'
}
Circle ($fx+$sensorX*$scale) ($fy+($h-$sensorY)*$scale) 5 '#073f55' '#ffffff'
for($x=13;$x -le 23;$x+=(Num 'vent_pitch')) { Rect ($fx+$x*$scale) ($fy+($h-30)*$scale) ((Num 'vent_slot_width')*$scale) (18*$scale) '#849db2' 'none' }
foreach($x in @($bossX,($w-$bossX))) { foreach($y in @((Num 'case_screw_bottom_y'),($h-(Num 'case_screw_top_offset')))) { Circle ($fx+$x*$scale) ($fy+($h-$y)*$scale) ((Num 'lid_screw_clearance')*$scale/2) '#efc274' '#916425' } }
$bayTop=$fy+($h-$baffleTop)*$scale; $bayBottom=$fy+($h-$baffleBottom)*$scale; $bayLeft=$fx+$baffleLeft*$scale
Line $bayLeft $bayTop ($right-$wall*$scale) $bayTop '#9561a0' 2 $true
Line $bayLeft $bayBottom ($right-$wall*$scale) $bayBottom '#9561a0' 2 $true
Line $bayLeft $bayTop $bayLeft $bayBottom '#9561a0' 2 $true
for($y=$ventY;$y -le $ventY+(Num 'sensor_vent_length')-(Num 'vent_slot_width')+0.0001;$y+=(Num 'vent_pitch')) { Rect ($right-$wall*$scale) ($fy+($h-$y-(Num 'vent_slot_width'))*$scale) ($wall*$scale) ((Num 'vent_slot_width')*$scale) '#498d96' 'none' }
$tongueX=$fx+($ux-(Num 'cable_tongue_width')/2)*$scale
Rect $tongueX $bottom ((Num 'cable_tongue_width')*$scale) ((Num 'cable_tongue_projection')*$scale) '#d3dce6' '#253348'
foreach($dx in @((-(Num 'cable_tie_slot_spacing')/2),((Num 'cable_tie_slot_spacing')/2))) {
    Rect ($fx+($ux+$dx-(Num 'cable_tie_slot_width')/2)*$scale) ($bottom+5*$scale) ((Num 'cable_tie_slot_width')*$scale) ((Num 'cable_tie_slot_length')*$scale) '#f6f7f9' '#52667c'
}
# Upright cradle shown as a front projection.
$standLeft=$fx-(Num 'stand_side_extension')*$scale
$shelfY=$bottom+$shelfBottom*$scale
Rect $standLeft ($shelfY-(Num 'stand_base_thickness')*$scale) ($standW*$scale) ((Num 'stand_base_thickness')*$scale) '#75889c' '#253348'
foreach($pedX in @($fx,($right-(Num 'stand_pedestal_width')*$scale))) {
    Rect $pedX $bottom ((Num 'stand_pedestal_width')*$scale) ((Num 'stand_under_case_clearance')*$scale) '#a5b2c1' '#253348'
    Rect $pedX ($bottom-(Num 'stand_guide_height')*$scale) ((Num 'stand_pedestal_width')*$scale) ((Num 'stand_guide_height')*$scale) '#a5b2c1' '#253348'
}
Line $fx ($fy-18) $right ($fy-18)
Line $fx ($fy-25) $fx ($fy-10)
Line $right ($fy-25) $right ($fy-10)
Label ($fx+130) ($fy-46) ((Fmt $w)+' mm') 17
Line 47 $fy 47 $bottom
Line 40 $fy 56 $fy
Line 40 $bottom 56 $bottom
Label 12 ($fy+200) (Fmt $h) 14
Label 12 ($fy+220) 'mm' 14
Label 145 ($shelfY+10) ('Cradle width '+(Fmt $standW)+' mm') 16

# Middle column labels deliberately separate assumptions from verified facts.
$tx=565
Label $tx 175 'Ambient sensor zone' 22 '#236e79' $true
Label $tx 210 'Front + right-side openings.' 18
Label $tx 240 'SHT40 case XY = 50.4, 21.4 mm.' 18
Line ($fx+$sensorX*$scale+10) ($fy+($h-$sensorY)*$scale) 540 255 '#498d96' 1.5
Label $tx 300 'Optional thermal baffle' 22 '#86518f' $true
Label $tx 335 'Dashed lines indicate a proposal.' 18
Label $tx 365 'Clears island; stays disabled.' 18
Label $tx 414 'Hardware stays provisional' 22 '#916425' $true
Label $tx 449 'Gold: case screws. Blue: PCB holes.' 18
Label $tx 479 'Orange: provisional 12 mm RF band.' 18
Label $tx 509 'Manufacturer plastic rule pending.' 18
Label $tx 565 'USB and shelf clearance' 22 '#415b77' $true
Label $tx 600 'USB exits the bottom (-Y).' 18
Label $tx 630 '18 x 10 mm plug-body passage.' 18
Label $tx 660 '16 x 8 mm budget; actual cable TBD.' 18
Label $tx 717 'Source checks only' 22 '#253348' $true
Label $tx 752 'M2.5 through-bolt mounts: ON' 18
Label $tx 782 'Fit / RF / thermal: NOT VERIFIED' 18 '#a55c00' $true

# Side section, Z goes right, Y goes up. Stand center is not filled in reality.
$sx=1060.0; $sy=$fy; $sw=$depth*$scale
Rect $sx $sy $sw ($h*$scale) '#e1e6ec' '#253348' 2
Rect ($sx+$floor*$scale) ($sy+$wall*$scale) (($body-$floor)*$scale) (($h-2*$wall)*$scale) '#ffffff' '#98a6b6'
Rect ($sx+$pz*$scale) ($sy+($h-$py-$ph)*$scale) ($pt*$scale) ($ph*$scale) '#b8d9cb' '#35745c'
Rect ($sx+($pz+$pt)*$scale) ($sy+($h-$py-$ph)*$scale+115) ((Num 'component_height_top')*$scale) 85 'none' '#8698a9' 1 $true
Label ($sx+$sw+22) 185 'Front lid' 17
Line ($sx+$sw-7) 216 ($sx+$sw+18) 204
Label ($sx+$sw+22) 284 'PCB' 17
Line ($sx+($pz+$pt/2)*$scale) 310 ($sx+$sw+18) 300
Label 1030 692 'Center route stays open' 17 '#415b77'
$standSideX=$sx-(Num 'stand_depth_extension')*$scale/2
Rect $standSideX ($shelfY-(Num 'stand_base_thickness')*$scale) ($standD*$scale) ((Num 'stand_base_thickness')*$scale) '#75889c' '#253348'
Rect ($sx-3*$scale) $bottom (($depth+6)*$scale) ((Num 'stand_under_case_clearance')*$scale) 'none' '#93a4b5' 1 $true
Label 1070 ($shelfY+10) ('Depth '+(Fmt $standD)+' mm') 16
Line $sx ($sy-18) ($sx+$sw) ($sy-18)
Line $sx ($sy-25) $sx ($sy-10)
Line ($sx+$sw) ($sy-25) ($sx+$sw) ($sy-10)
Label ($sx+44) ($sy-46) ((Fmt $depth)+' mm') 17
Line ($sx+$sw+140) $sy ($sx+$sw+140) $shelfY
Label 1390 536 (Fmt $shelfHeight) 17
Label 1390 561 'mm total' 15
Label 42 896 'All dimensions are mm and adjustable. No PCB/module fit, antenna clearance, thermal performance, or printability is certified.' 18 '#a55c00'
Label 42 924 'Source: sensor_enclosure.scad  |  Coordinate convention: X right, Y up, Z back-to-front  |  See mechanical_interface.json' 16 '#52667c'
[void]$svg.AppendLine('</svg>')
$svgPath=Join-Path $root 'concept_reference.svg'
$pngPath=Join-Path $root 'concept_reference.png'
[IO.File]::WriteAllText($svgPath,$svg.ToString(),[Text.UTF8Encoding]::new($false))
$bitmap.Save($pngPath,[Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose(); $bitmap.Dispose()
[xml]$svgXml=Get-Content -LiteralPath $svgPath -Raw
Check 'Generated schematic SVG parses as XML' ($svgXml.DocumentElement.LocalName -eq 'svg') 'Source-derived orthographic schematic, not CAD render'
$report=[ordered]@{
    generated_utc=[DateTime]::UtcNow.ToString('o')
    source_sha256=(Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash
    overall_static_checks_passed=(@($checks | Where-Object {!$_.passed}).Count -eq 0)
    check_count=$checks.Count
    scope='Source delimiters, selected scalar dimensional constraints, release gates, and schematic XML only'
    not_verified=@('OpenSCAD parsing','Boolean geometry','watertight/manifold mesh','slicing','actual board/USB fit','antenna clearance','thermal performance','physical print')
    input_sha256=(Get-FileHash -LiteralPath (Join-Path $root 'pcb_A1_mechanical_interface.json') -Algorithm SHA256).Hash
    dimensions_mm=[ordered]@{case=@($w,$h,$depth);pcb_A1=@($pw,$ph,$pt);stand=@($standW,$standD,$standH);shelf_height=$shelfHeight;usb_mouth=@($ux,$uy,$uz);sensor_top_center=@($sensorX,$sensorY,$sensorZ);holes_case=$holesCase}
    checks=$checks
}
$report | ConvertTo-Json -Depth 9 | Set-Content -LiteralPath (Join-Path $root 'validation_report.json') -Encoding utf8
$checks | Format-Table name,passed -AutoSize
Write-Output ('Static checks: '+$checks.Count+'; passed: '+$report.overall_static_checks_passed)
Write-Output 'Static scope only; see provisional_cad reports for CAD/mesh results. Physical fit remains unverified.'
if(!$report.overall_static_checks_passed){exit 1}
