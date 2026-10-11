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
$source=Join-Path $PSScriptRoot 'sensor_enclosure.scad'
$out=Join-Path $PSScriptRoot 'provisional_cad'
$records=@()
foreach($part in @('base','lid','stand','wall_spacer','coupon')) {
  $target=Join-Path $out ($part+'_PROVISIONAL.stl')
  $cadArgs=@('--hardwarnings','--export-format','binstl','-D','acknowledge_provisional_render=true','-D',('part="'+$part+'"'),'-o',$target,$source)
  $lines=& $cadExe @cadArgs 2>&1
  $code=$LASTEXITCODE
  $log=$lines | Out-String
  $log | Set-Content -LiteralPath (Join-Path $out ($part+'_render.log'))
  $ok=$code -eq 0 -and $log -match 'Simple:\s+yes' -and $log -notmatch 'ERROR:|WARNING:' -and (Test-Path -LiteralPath $target)
  $records+=[pscustomobject]@{part=$part;passed=$ok;process_exit_code=$code;file=$target}
  Write-Output ($part+': CGAL simple solid = '+$ok)
  if(!$ok){throw ('Rendering failed: '+$part)}
}
foreach($part in @('base','lid','stand','shelf_assembly')) {
  $cadArgs=@('--hardwarnings','--render','--imgsize','1400,1100','--autocenter','--viewall','--projection','o','--camera','0,0,0,55,0,30,250','-D','acknowledge_provisional_render=true','-D','show_reference_board=false','-D','show_keepouts=false','-D','show_hardware=false','-D',('part="'+$part+'"'),'-o',(Join-Path $out ($part+'_render.png')),$source)
  if($part -eq 'shelf_assembly') {
    $cadArgs=@('--hardwarnings','--render','--imgsize','1400,1400','--projection','o','--camera','41.9,25,52.4,65,0,25,350','-D','acknowledge_provisional_render=true','-D','show_reference_board=false','-D','show_keepouts=false','-D','show_hardware=false','-D','part="shelf_assembly"','-o',(Join-Path $out ($part+'_render.png')),$source)
  }
  $lines=& $cadExe @cadArgs 2>&1
  if($LASTEXITCODE -ne 0){throw ('Image render failed: '+$part)}
  $lines | Out-String | Set-Content -LiteralPath (Join-Path $out ($part+'_image.log'))
}
[ordered]@{source_sha256=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash;generated_utc=[datetime]::UtcNow.ToString('o');passed=$true;renderer='Official portable OpenSCAD 2021.01';parts=$records} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $out 'render_validation.json') -Encoding utf8
