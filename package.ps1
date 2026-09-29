# Build and Package TokenViewer Pro
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot

Write-Host "Building TokenViewer Pro with PyInstaller..." -ForegroundColor Cyan
pyinstaller --clean -y TokenViewerPro.spec

$exeDir = Join-Path $root 'dist\TokenViewerPro'
if (-not (Test-Path $exeDir)) {
    Write-Host "Build failed, output dir not found!" -ForegroundColor Red
    exit 1
}

Copy-Item (Join-Path $root 'icon.ico') (Join-Path $exeDir 'icon.ico') -Force
Copy-Item (Join-Path $root 'icon.png') (Join-Path $exeDir 'icon.png') -Force

Write-Host "Creating shortcuts..." -ForegroundColor Cyan
& (Join-Path $root 'make_shortcut.ps1')

Write-Host "Build & Packaging completed successfully!" -ForegroundColor Green
