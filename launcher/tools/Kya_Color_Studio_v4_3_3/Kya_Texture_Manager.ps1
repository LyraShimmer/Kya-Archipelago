param(
  [ValidateSet('Apply','RestoreVanilla')]
  [string]$Action = 'Apply',
  [string]$SourcePNG = '',
  [string]$Destination = ''
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$name = '5417b68a93e1b617-435f677b690903da-00002213.png'
$statePath = Join-Path $root 'COLOR_STUDIO_STATE.json'
try {
  if (-not $Destination) { throw 'Destination is required.' }
  $dest = [IO.Path]::GetFullPath($Destination.Trim().Trim('"'))
  if ($dest -notmatch '(?i)[\\/]SLES-51473[\\/]replacements[\\/]?$') {
    throw 'The selected path must end with SLES-51473\replacements.'
  }
  if (-not (Test-Path -LiteralPath $dest -PathType Container)) { throw ('Folder not found: ' + $dest) }
  $target = Join-Path $dest $name
  if (Test-Path -LiteralPath $statePath -PathType Leaf) {
    $prior=Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
    if ([IO.Path]::GetFullPath($prior.Destination).TrimEnd([char[]]@('\','/')) -ne $dest.TrimEnd([char[]]@('\','/'))) {
      throw ('Existing backup belongs to another folder: ' + $prior.Destination)
    }
  }

  if ($Action -eq 'Apply') {
    $src = [IO.Path]::GetFullPath($SourcePNG.Trim().Trim('"'))
    if (-not (Test-Path -LiteralPath $src -PathType Leaf)) { throw ('PNG not found: '+$src) }
    $stream = [IO.File]::OpenRead($src)
    try {
       $signature = New-Object byte[] 8
       if ($stream.Read($signature,0,8) -ne 8) { throw 'Truncated PNG file.' }
       if ([BitConverter]::ToString($signature) -ne '89-50-4E-47-0D-0A-1A-0A') { throw 'Invalid PNG file.' }
    } finally { $stream.Close() }
    if (Test-Path -LiteralPath $statePath -PathType Leaf) {
       $s=Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
       if ([IO.Path]::GetFullPath($s.Destination).TrimEnd([char[]]@('\','/')) -ne $dest.TrimEnd([char[]]@('\','/'))) {
          throw ('A backup is active for another folder: '+$s.Destination+'. Use Restore Vanilla there first.')
       }
    } else {
       $backup=Join-Path $root ('backup_'+(Get-Date -Format 'yyyyMMdd_HHmmss_fff'))
       New-Item -Path $backup -ItemType Directory -ErrorAction Stop | Out-Null
       $existed=Test-Path -LiteralPath $target -PathType Leaf
       if ($existed) { Copy-Item -LiteralPath $target -Destination (Join-Path $backup $name) -ErrorAction Stop }
       [PSCustomObject]@{Destination=$dest;Backup=$backup;Existed=[bool]$existed} | ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding UTF8
    }
    Copy-Item -LiteralPath $src -Destination $target -Force -ErrorAction Stop
    Write-Output ('Applied: ' + $name)
  } elseif ($Action -eq 'RestoreVanilla') {
    # PCSX2 uses game-native pixels when the replacement file is absent.
    # Back up a pre-existing file even if a Studio backup/state does not exist.
    if (Test-Path -LiteralPath $target -PathType Leaf) {
       if (-not (Test-Path -LiteralPath $statePath -PathType Leaf)) {
          $backup=Join-Path $root ('backup_before_vanilla_'+(Get-Date -Format 'yyyyMMdd_HHmmss_fff'))
          New-Item -Path $backup -ItemType Directory -ErrorAction Stop | Out-Null
          Copy-Item -LiteralPath $target -Destination (Join-Path $backup $name) -ErrorAction Stop
          Write-Output ('Previous replacement saved: '+$backup)
       }
       Remove-Item -LiteralPath $target -Force -ErrorAction Stop
       Write-Output ('Vanilla enabled: replacement removed: '+$name)
    } else { Write-Output 'Vanilla already active: replacement is absent.' }
    if (Test-Path -LiteralPath $statePath -PathType Leaf) {
       $s=Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
       if ([IO.Path]::GetFullPath($s.Destination).TrimEnd([char[]]@('\','/')) -ne $dest.TrimEnd([char[]]@('\','/'))) {
          throw ('Backup belongs to another folder: '+$s.Destination)
       }
       Remove-Item -LiteralPath $statePath -Force
       Write-Output ('Older backup retained at: '+$s.Backup)
    }
  }
  Write-Output 'Restart PCSX2/game to refresh cached textures.'
} catch {
  Write-Error ('ERROR: '+$_.Exception.Message)
  exit 1
}
