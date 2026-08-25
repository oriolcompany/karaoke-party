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
    $shortcut.TargetPath = $Target
    $shortcut.WorkingDirectory = $RepoRoot
    $shortcut.IconLocation = "$ico,0"
    $shortcut.Description = "Karaoke Party"
    $shortcut.Save()
}

Save-KaraokeShortcut (Join-Path $RepoRoot "Karaoke Party.lnk")

$desktop = [Environment]::GetFolderPath("Desktop")
if ($desktop) {
    Save-KaraokeShortcut (Join-Path $desktop "Karaoke Party.lnk")
}
