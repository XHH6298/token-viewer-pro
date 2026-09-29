# Create Desktop and Start Menu shortcuts for TokenViewer Pro.
$ErrorActionPreference = 'Stop'

$target = Join-Path $PSScriptRoot 'dist\TokenViewerPro\TokenViewerPro.exe'
if (-not (Test-Path $target)) {
    Write-Host "Not found: $target. Build onedir package first." -ForegroundColor Red
    exit 1
}
$icoFile = Join-Path $PSScriptRoot 'dist\TokenViewerPro\icon.ico'
if (-not (Test-Path $icoFile)) {
    $icoFile = Join-Path $PSScriptRoot 'icon.ico'
}

$desktop = [Environment]::GetFolderPath('Desktop')
$workspaceRoot = Split-Path $PSScriptRoot -Parent
$startMenu = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs'

function New-Link($path, $name) {
    $ws = New-Object -ComObject WScript.Shell
    $lnkPath = Join-Path $path "$name.lnk"
    if (Test-Path $lnkPath) {
        Remove-Item $lnkPath -Force -ErrorAction SilentlyContinue
    }
    $lnk = $ws.CreateShortcut($lnkPath)
    $lnk.TargetPath = $target
    $lnk.WorkingDirectory = Split-Path $target
    $lnk.IconLocation = "$icoFile,0"
    $lnk.Description = 'TokenViewer Pro - macOS/VisionOS 空间毛玻璃桌面仪表盘'
    $lnk.Save()
    Write-Host "Created: $lnkPath"
}

New-Link $workspaceRoot 'TokenViewer Pro'
New-Link $desktop        'TokenViewer Pro'
New-Link $startMenu      'TokenViewer Pro'

$sig = '[DllImport("shell32.dll")] public static extern void SHChangeNotify(int wEventId, int uFlags, IntPtr dwItem1, IntPtr dwItem2);'
Add-Type -MemberDefinition $sig -Name "ShellHelper" -Namespace "Win32" -ErrorAction SilentlyContinue
[Win32.ShellHelper]::SHChangeNotify(0x08000000, 0, [IntPtr]::Zero, [IntPtr]::Zero)
Write-Host "Desktop and Start Menu shortcuts updated!"
