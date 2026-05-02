Write-Host "=== SimpleClock Build ===" -ForegroundColor Cyan

uv run pyinstaller --onefile --windowed --name SimpleClock --clean main.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build FAILED (exit $LASTEXITCODE)" -ForegroundColor Red
    exit $LASTEXITCODE
}

$exe = "dist\SimpleClock.exe"
if (-not (Test-Path $exe)) {
    Write-Host "Build output not found: $exe" -ForegroundColor Red
    exit 1
}

$sizeMB = [math]::Round((Get-Item $exe).Length / 1MB, 1)
Write-Host "Build succeeded: $exe ($sizeMB MB)" -ForegroundColor Green

if ($sizeMB -lt 30) {
    Write-Host "WARNING: EXE is only ${sizeMB} MB — Qt plugins may be missing. Consider adding --collect-all PyQt6." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "*** SMOKE TEST REMINDER ***" -ForegroundColor Yellow
Write-Host "Copy dist\SimpleClock.exe to a Windows Sandbox, VM, or user account"
Write-Host "that has NO Python or Qt installed, then double-click."
Write-Host "Expected: window appears with no DLL errors."
Write-Host "If it crashes: rerun with --collect-all PyQt6 added to this script."
