#Requires -Version 5.0
# ZeeTech Flutter App - Complete Rebuild Script (Windows PowerShell)
# Run this script to rebuild the app with all 401 error fixes

Write-Host '==========================================' -ForegroundColor Cyan
Write-Host 'ZeeTech Flutter App - Rebuild & Test' -ForegroundColor Cyan
Write-Host '==========================================' -ForegroundColor Cyan
Write-Host ''

# Check Flutter is installed
Write-Host '[1/5] Checking Flutter installation...' -ForegroundColor Yellow
$flutterPath = (Get-Command flutter -ErrorAction SilentlyContinue).Source
if (-not $flutterPath) {
  Write-Host 'ERROR: Flutter not found' -ForegroundColor Red
  Write-Host 'Please install Flutter and add it to PATH'
  exit 1
}
Write-Host "✓ Flutter found at: $flutterPath" -ForegroundColor Green
Write-Host ''

# Navigate to app directory
Write-Host '[2/5] Navigating to zeetech directory...' -ForegroundColor Yellow
$appDir = 'c:\Users\numl-\OneDrive\Desktop\zeetech2\zeetech'
if (-not (Test-Path $appDir)) {
  Write-Host "ERROR: Directory not found: $appDir" -ForegroundColor Red
  exit 1
}
Set-Location $appDir
Write-Host "✓ Current directory: $(Get-Location)" -ForegroundColor Green
Write-Host ''

# Clean build artifacts
Write-Host '[3/5] Cleaning old build artifacts...' -ForegroundColor Yellow
& flutter clean
Write-Host '✓ Clean complete' -ForegroundColor Green
Write-Host ''

# Get dependencies
Write-Host '[4/5] Downloading dependencies...' -ForegroundColor Yellow
& flutter pub get
Write-Host '✓ Dependencies downloaded' -ForegroundColor Green
Write-Host ''

# Verify critical dependencies
Write-Host '[5/5] Verifying critical dependencies...' -ForegroundColor Yellow

$pubList = & flutter pub list
$hasPathProvider = $pubList | Select-String 'path_provider'
$hasDioCookieManager = $pubList | Select-String 'dio_cookie_manager'
$hasCookieJar = $pubList | Select-String 'cookie_jar'
$hasDio = $pubList | Select-String '^dio'

if ($hasPathProvider) {
  Write-Host '✓ path_provider is installed' -ForegroundColor Green
}
else {
  Write-Host '✗ ERROR: path_provider not found!' -ForegroundColor Red
  exit 1
}

if ($hasDioCookieManager) {
  Write-Host '✓ dio_cookie_manager is installed' -ForegroundColor Green
}
else {
  Write-Host '✗ ERROR: dio_cookie_manager not found!' -ForegroundColor Red
  exit 1
}

if ($hasCookieJar) {
  Write-Host '✓ cookie_jar is installed' -ForegroundColor Green
}
else {
  Write-Host '✗ ERROR: cookie_jar not found!' -ForegroundColor Red
  exit 1
}

if ($hasDio) {
  Write-Host '✓ dio is installed' -ForegroundColor Green
}
else {
  Write-Host '✗ ERROR: dio not found!' -ForegroundColor Red
  exit 1
}

Write-Host ''
Write-Host '==========================================' -ForegroundColor Green
Write-Host '✓ ALL CHECKS PASSED' -ForegroundColor Green
Write-Host '==========================================' -ForegroundColor Green
Write-Host ''
Write-Host 'Ready to run app!' -ForegroundColor Green
Write-Host ''
Write-Host 'Next step: Run this command to start the app' -ForegroundColor Cyan
Write-Host '  flutter run' -ForegroundColor White
Write-Host ''
Write-Host 'After app starts, test provider service creation:' -ForegroundColor Cyan
Write-Host '  1. Provider Login (use your credentials)' -ForegroundColor White
Write-Host '  2. Navigate to Manage Services → Add Service' -ForegroundColor White
Write-Host '  3. Enter service details (name, price, description)' -ForegroundColor White
Write-Host '  4. Click Add Service button' -ForegroundColor White
Write-Host '  5. Should succeed with NO 401 error' -ForegroundColor White
Write-Host ''
