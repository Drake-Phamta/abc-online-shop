# Handler of the link type abcshop: used by the showcase pages when they are opened from this computer.
#   abcshop:start             run CHAY_DEMO.bat (the demo server) in its own window
#   abcshop:reveal?p=<path>   show a file or folder of this project in File Explorer
#   abcshop:open?p=<path>     open a Visual Paradigm project (.vpp) of this project
# <path> is relative to the project folder. Anything outside the project folder, or any other action, is refused.
# CHAY_DEMO.bat registers the handler for the current Windows user on every run (abcshop.ps1 -Register), so it always
# points to this copy of the project. To remove it: reg delete "HKCU\Software\Classes\abcshop" /f
# Keep this file ASCII only: Windows PowerShell 5.1 reads a script without BOM in the ANSI code page.
#   -DryRun prints what a link would do instead of doing it (used to check the handler).
param([string]$Url = "", [switch]$Register, [switch]$DryRun)

$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))

if ($Register) {
    $exe = Join-Path $env:SystemRoot "System32\WindowsPowerShell\v1.0\powershell.exe"
    $command = '"' + $exe + '" -NoProfile -ExecutionPolicy RemoteSigned -WindowStyle Hidden -File "' + $PSCommandPath + '" "%1"'
    $key = [Microsoft.Win32.Registry]::CurrentUser.CreateSubKey("Software\Classes\abcshop")
    $key.SetValue("", "URL:ABC Online Shop showcase")
    $key.SetValue("URL Protocol", "")
    $cmd = $key.CreateSubKey("shell\open\command")
    $cmd.SetValue("", $command)
    $cmd.Close()
    $key.Close()
    exit 0
}

function Refuse($why) { if ($DryRun) { "refused: $why" }; exit 1 }
function Run($file, $arguments) {
    if ($DryRun) { "run: $file $arguments"; return }
    if ($arguments) { Start-Process -FilePath $file -ArgumentList $arguments } else { Start-Process -FilePath $file -WorkingDirectory $root }
}

if ($Url -notmatch '^abcshop:(?://)?(start|reveal|open)/?(?:\?p=([^&]*))?$') { Refuse "unknown link" }
$action = $Matches[1]
$rel = if ($Matches[2]) { [Uri]::UnescapeDataString($Matches[2]) } else { "" }

if ($action -eq "start") { Run (Join-Path $root "CHAY_DEMO.bat") $null; exit 0 }

# reveal and open: the path must stay inside the project folder and exist
$rel = $rel.Replace("/", "\").TrimStart("\")
if ($rel -eq "" -or $rel -match ':') { Refuse "empty or absolute path" }
$full = [IO.Path]::GetFullPath((Join-Path $root $rel)).TrimEnd("\")
if (-not $full.StartsWith($root.TrimEnd("\") + "\", [StringComparison]::OrdinalIgnoreCase)) { Refuse "outside the project folder" }
if (-not (Test-Path -LiteralPath $full)) { Refuse "no such file" }

if ($action -eq "reveal") {
    if (Test-Path -LiteralPath $full -PathType Container) { Run "explorer.exe" ('"' + $full + '"') }
    else { Run "explorer.exe" ('/select,"' + $full + '"') }
} elseif ([IO.Path]::GetExtension($full) -ieq ".vpp") {
    Run $full $null
} else {
    Refuse "only a .vpp project can be opened"
}
exit 0
