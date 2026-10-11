param([string]$OpenScadPath = $env:OPENSCAD_EXE)
$ErrorActionPreference='Stop'
if (-not $OpenScadPath) {
  $command = Get-Command openscad.com -ErrorAction SilentlyContinue
  if ($command) { $OpenScadPath = $command.Source }
}
if (-not $OpenScadPath -or -not (Test-Path -LiteralPath $OpenScadPath)) {
  throw 'Set -OpenScadPath or OPENSCAD_EXE to an existing OpenSCAD executable.'
}
$cadExe = $OpenScadPath
$sourcePath=Join-Path $PSScriptRoot 'sensor_enclosure.scad'
$out=Join-Path $PSScriptRoot 'provisional_cad'
$source=Get-Content -LiteralPath $sourcePath -Raw
$cut=$source.LastIndexOf("`nchecks();")
if($cut -lt 0){throw 'Expected main-dispatch boundary not found'}
$testCode=@"

checks();
module closed_shell() { base(); translate([0,0,body_depth]) lid(); }
module placed_in_stand() {
  translate([stand_side_extension,stand_slot_y+stand_fit_clearance+case_depth,stand_case_bottom_z])
    rotate([90,0,0]) children();
}
module nominal_board() {
  difference() {
    translate(pcb_origin) cube([pcb_width,pcb_height,pcb_thickness]);
    for(p=pcb_holes) translate([pcb_origin[0]+p[0],pcb_origin[1]+p[1],pcb_origin[2]-eps])
      cylinder(d=pcb_hole_drill,h=pcb_thickness+2*eps);
  }
}
module nominal_components() {
  translate(module_case_origin) cube(module_size);
  translate([usb_x-usb_shell_width/2,usb_mouth_case[1],pcb_origin[2]+pcb_thickness])
    cube([usb_shell_width,usb_shell_depth,usb_shell_height]);
  translate([sensor_case[0]-sensor_body_width/2,sensor_case[1]-sensor_body_width/2,pcb_origin[2]+pcb_thickness])
    cube([sensor_body_width,sensor_body_width,sensor_body_height+sensor_minimum_free_air]);
}
module metal() { pcb_hardware(); case_hardware(); }
if(validation_test=="base_lid") intersection(){base();translate([0,0,body_depth])lid();}
else if(validation_test=="stand_shell") intersection(){stand();placed_in_stand()closed_shell();}
else if(validation_test=="nominal_board_components") intersection(){closed_shell();union(){nominal_board();nominal_components();}}
else if(validation_test=="hardware_plastic") intersection(){closed_shell();metal();}
else if(validation_test=="pcb_hardware_board") intersection(){nominal_board();pcb_hardware();}
else if(validation_test=="hardware_components") intersection(){nominal_components();metal();}
else if(validation_test=="usb_body_shell") intersection(){closed_shell();usb_plug_body_sweep(usb_plug_clearance);}
else if(validation_test=="usb_insertion_stand") intersection(){stand();placed_in_stand()usb_plug_insertion_sweep(usb_plug_clearance);}
else if(validation_test=="hardware_stand") intersection(){stand();placed_in_stand()metal();}
else if(validation_test=="hardware_rf") intersection(){metal();union(){for(b=rf_reservation_boxes)translate(b[0])cube(b[1]);}}
else if(validation_test=="hardware_sensor_region") intersection(){metal();translate([sensor_island_min[0],sensor_island_min[1],0])cube([sensor_island_max[0]-sensor_island_min[0],sensor_island_max[1]-sensor_island_min[1],case_depth]);}
else assert(false,"Unknown collision check");
"@
$validationSource=Join-Path $out 'assembly_collision_checks.scad'
[IO.File]::WriteAllText($validationSource,$source.Substring(0,$cut)+$testCode,[Text.UTF8Encoding]::new($false))
function Get-ScadNumber([string]$name) {
  $match=[regex]::Match($source,'(?m)^'+[regex]::Escape($name)+'\s*=\s*([\d.]+)')
  if(!$match.Success){throw "Missing numeric parameter: $name"}
  return [double]::Parse($match.Groups[1].Value,[Globalization.CultureInfo]::InvariantCulture)
}
$pcbBottom=(Get-ScadNumber floor_thickness)+(Get-ScadNumber pcb_support_height)
$pcbTop=$pcbBottom+(Get-ScadNumber pcb_thickness)
$bodyDepth=Get-ScadNumber body_depth
$allowedPlanes=@{
  stand_shell=@((Get-ScadNumber stand_base_thickness)+(Get-ScadNumber stand_under_case_clearance))
  nominal_board_components=@($pcbBottom)
  hardware_plastic=@(($bodyDepth+(Get-ScadNumber lid_thickness)),($bodyDepth-(Get-ScadNumber case_nut_roof)))
  pcb_hardware_board=@($pcbTop)
}
function Test-PlanarContact([string]$path,[double[]]$planes) {
  if(!$planes.Count -or !(Test-Path -LiteralPath $path)){return $false}
  $lines=@(Get-Content -LiteralPath $path | Where-Object {$_.Trim() -and !$_.Trim().StartsWith('#')})
  $header=$lines[0].Trim() -split '\s+'
  if($header[0] -ne 'OFF'){return $false}
  $start=1
  if($header.Count -ge 4){$counts=$header[1..3]}else{$counts=$lines[1].Trim() -split '\s+';$start=2}
  $nv=[int]$counts[0];$nf=[int]$counts[1]
  if($nv -le 0 -or $nf -le 0){return $false}
  $zs=@(for($i=0;$i -lt $nv;$i++) { $v=$lines[$start+$i].Trim() -split '\s+'; [double]::Parse($v[2],[Globalization.CultureInfo]::InvariantCulture) })
  # Every whole face must lie on a permitted contact plane; vertices alone could miss a spanning volume.
  for($i=0;$i -lt $nf;$i++) {
    $f=$lines[$start+$nv+$i].Trim() -split '\s+'
    $matched=$false
    foreach($plane in $planes) {
      $onPlane=$true
      for($j=1;$j -le [int]$f[0];$j++) {if([math]::Abs($zs[[int]$f[$j]]-$plane) -gt 0.00001){$onPlane=$false}}
      if($onPlane){$matched=$true}
    }
    if(!$matched){return $false}
  }
  return $true
}
$tests=@('base_lid','stand_shell','nominal_board_components','hardware_plastic','pcb_hardware_board','hardware_components','usb_body_shell','usb_insertion_stand','hardware_stand','hardware_rf','hardware_sensor_region')
$results=@()
foreach($test in $tests) {
  $offPath=Join-Path $out ($test+'_intersection.off')
  if(Test-Path -LiteralPath $offPath){Remove-Item -LiteralPath $offPath}
  $cadArgs=@('--hardwarnings','-D','acknowledge_provisional_render=true','-D',('validation_test="'+$test+'"'),'-o',$offPath,$validationSource)
  $lines=& $cadExe @cadArgs 2>&1
  $code=$LASTEXITCODE
  $log=($lines | Out-String)
  [IO.File]::WriteAllText((Join-Path $out ($test+'_intersection.log')),$log)
  $empty=$log -match 'Current top level object is empty' -and $log -notmatch 'ERROR:|WARNING:'
  $planar=$false
  if($allowedPlanes.ContainsKey($test) -and $log -notmatch 'ERROR:') {
    $planar=Test-PlanarContact $offPath $allowedPlanes[$test]
    $unexpectedWarnings=@($lines | Where-Object {"$_" -match 'WARNING:' -and "$_" -notmatch 'Object may not be a valid 2-manifold'})
    if($unexpectedWarnings.Count){$planar=$false}
  }
  $passed=$empty -or $planar
  $results+=[pscustomobject]@{test=$test;passed=$passed;empty_intersection=$empty;expected_planar_contact=$planar;allowed_contact_z=$allowedPlanes[$test];process_exit_code=$code}
  Write-Output ($test+': passed = '+$passed+'; empty = '+$empty+'; planar contact = '+$planar)
}
$report=[ordered]@{source_sha256=(Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash;generated_utc=[datetime]::UtcNow.ToString('o');passed=(@($results | Where-Object {!$_.passed}).Count -eq 0);scope='Nominal plastic, PCB with actual holes, selected hardware envelopes, module/USB/SHT40 boxes, and explicit plug-body gauges. Expected zero-thickness contact is checked per OFF face. Excludes routed components, threads, actual cable/bend and physical tolerances.';checks=$results}
$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $out 'collision_validation.json') -Encoding utf8
if(!$report.passed){throw 'An intersection was nonempty or computation failed; inspect logs.'}
