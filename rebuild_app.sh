#!/bin/bash
# ZeeTech Flutter App - Complete Rebuild & Test Script
# This script will rebuild the Flutter app with all 401 error fixes

set -e  # Exit on any error

echo "=========================================="
echo "ZeeTech Flutter App - Rebuild & Test"
echo "=========================================="
echo ""

# Check Flutter is installed
echo "[1/5] Checking Flutter installation..."
if ! command -v flutter &> /dev/null; then
    echo "ERROR: Flutter not found. Please install Flutter first."
    exit 1
fi
echo "✓ Flutter found at: $(which flutter)"
echo ""

# Navigate to app directory
echo "[2/5] Navigating to zeetech directory..."
cd c:/Users/numl-/OneDrive/Desktop/zeetech2/zeetech || exit 1
echo "✓ Current directory: $(pwd)"
echo ""

# Clean build artifacts
echo "[3/5] Cleaning old build artifacts..."
flutter clean
echo "✓ Clean complete"
echo ""

# Get dependencies
echo "[4/5] Downloading dependencies..."
flutter pub get
echo "✓ Dependencies downloaded"
echo ""

# Verify path_provider is installed
echo "[5/5] Verifying critical dependencies..."
if flutter pub list | grep -q "path_provider"; then
    echo "✓ path_provider is installed"
else
    echo "✗ ERROR: path_provider not found!"
    exit 1
fi

if flutter pub list | grep -q "dio_cookie_manager"; then
    echo "✓ dio_cookie_manager is installed"
else
    echo "✗ ERROR: dio_cookie_manager not found!"
    exit 1
fi

if flutter pub list | grep -q "cookie_jar"; then
    echo "✓ cookie_jar is installed"
else
    echo "✗ ERROR: cookie_jar not found!"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ ALL CHECKS PASSED"
echo "=========================================="
echo ""
echo "Ready to run app!"
echo ""
echo "Run this command to start the app:"
echo "  flutter run"
echo ""
echo "After app starts, test provider service creation:"
echo "  1. Provider Login"
echo "  2. Manage Services → Add Service"  
echo "  3. Enter service details and click Add"
echo "  4. Should succeed (no 401 error)"
echo ""
