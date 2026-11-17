param(
    [Parameter(Mandatory = $true)][string]$RepoRoot,
    [Parameter(Mandatory = $true)][string]$Target
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$ico = Join-Path $RepoRoot "web\icon.ico"
if (-not (Test-Path -LiteralPath $ico)) {
    exit 0
}

function Save-KaraokeShortcut([string]$Path) {
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($Path)
    # cmd.exe always opens a real console. Pointing the shortcut at the .bat
    # could keep a minimized style inherited from a hidden creator process.
    $shortcut.TargetPath = Join-Path $env:SystemRoot "System32\cmd.exe"
    $shortcut.Arguments = "/d /c call `"$Target`""
    $shortcut.WorkingDirectory = $RepoRoot
    $shortcut.WindowStyle = 1
    $shortcut.IconLocation = "$ico,0"
    $shortcut.Description = "Karaoke Party"
    $shortcut.Save()
}

Save-KaraokeShortcut (Join-Path $RepoRoot "Karaoke Party.lnk")

$desktop = [Environment]::GetFolderPath("Desktop")
if ($desktop) {
    Save-KaraokeShortcut (Join-Path $desktop "Karaoke Party.lnk")
}
