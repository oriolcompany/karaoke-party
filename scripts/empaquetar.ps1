param(
    [string]$RepoRoot = ""
)

$ErrorActionPreference = "Stop"

if (-not $RepoRoot) {
    $RepoRoot = Split-Path -Parent $PSScriptRoot
}
$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path

function Get-NextPackVersion([string]$Root) {
    $highest = 0
    Get-ChildItem -LiteralPath $Root -Filter "Karaoke_Party_v*.zip" -File -ErrorAction SilentlyContinue | ForEach-Object {
        if ($_.Name -match '^Karaoke_Party_v(\d+)\.zip$') {
            $number = [int]$Matches[1]
            if ($number -gt $highest) {
                $highest = $number
            }
        }
    }
    return $highest + 1
}

function Copy-PackTree([string]$Source, [string]$Destination) {
    if (-not (Test-Path -LiteralPath $Source)) {
        throw "No s'ha trobat $Source"
    }
    New-Item -ItemType Directory -Force -Path $Destination | Out-Null
    # Robocopy codes 0-7 mean the copy succeeded.
    & robocopy $Source $Destination /E /NFL /NDL /NJH /NJS /NC /NS /NP /XD __pycache__ .pytest_cache /XF *.pyc *.pyo | Out-Null
    if ($LASTEXITCODE -ge 8) {
        throw "No s'ha pogut copiar $Source (robocopy $LASTEXITCODE)"
    }
}

$version = Get-NextPackVersion $RepoRoot
$name = "Karaoke_Party_v$version"
$zipPath = Join-Path $RepoRoot "$name.zip"
if (Test-Path -LiteralPath $zipPath) {
    throw "Ja existeix $zipPath"
}

$stageParent = Join-Path ([System.IO.Path]::GetTempPath()) ("karaoke-pack-" + [guid]::NewGuid().ToString("N"))
$stage = Join-Path $stageParent $name
New-Item -ItemType Directory -Force -Path $stage | Out-Null

try {
    foreach ($dir in @("src", "web", "scripts", "vendor")) {
        Copy-PackTree (Join-Path $RepoRoot $dir) (Join-Path $stage $dir)
    }

    foreach ($file in @("KaraokeParty.bat", "pyproject.toml", "README.md")) {
        $source = Join-Path $RepoRoot $file
        if (-not (Test-Path -LiteralPath $source)) {
            throw "No s'ha trobat $file"
        }
        Copy-Item -LiteralPath $source -Destination (Join-Path $stage $file)
    }

    # The packager itself is only for this PC.
    $ownScript = Join-Path $stage "scripts\empaquetar.ps1"
    if (Test-Path -LiteralPath $ownScript) {
        Remove-Item -LiteralPath $ownScript -Force
    }

    Get-ChildItem -LiteralPath $stage -Recurse -Force -Directory |
        Where-Object { $_.Name -eq "__pycache__" -or $_.Name -like "*.egg-info" -or $_.Name -eq ".pytest_cache" } |
        Sort-Object FullName -Descending |
        ForEach-Object { Remove-Item -LiteralPath $_.FullName -Recurse -Force }

    if (Test-Path -LiteralPath $zipPath) {
        Remove-Item -LiteralPath $zipPath -Force
    }
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::CreateFromDirectory(
        $stageParent,
        $zipPath,
        [System.IO.Compression.CompressionLevel]::Optimal,
        $false
    )
}
finally {
    if (Test-Path -LiteralPath $stageParent) {
        Remove-Item -LiteralPath $stageParent -Recurse -Force
    }
}

$info = Get-Item -LiteralPath $zipPath
Write-Output $zipPath
Write-Output ("{0:N1} MB" -f ($info.Length / 1MB))
exit 0
