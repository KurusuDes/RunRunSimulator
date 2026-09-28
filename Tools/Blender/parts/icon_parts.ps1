param([string]$Names = '*', [string]$Tmp = (Join-Path $env:TEMP 'monchi_icons'))
$Blender = 'C:\Program Files\Blender Foundation\Blender 4.5\blender.exe'
$Script = Join-Path $PSScriptRoot 'icon_part.py'
& $Blender --background --factory-startup --python $Script -- $Names $Tmp | Select-String 'ICON_DONE|ICON_FAIL|Traceback|Error'
python $Script $Tmp
