@echo off
REM ZeeTech Backend + Frontend Quick Start Script
REM This script helps you set up and run the entire ZeeTech application

echo.
echo ========================================
echo   ZeeTech Backend Setup Script
echo ========================================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed. Please install Node.js 16+ first.
    echo Download from: https://nodejs.org/
    exit /b 1
)

echo [✓] Node.js found: %cd%\node.exe

REM Navigate to backend
cd backend

echo.
echo ========================================
echo   Installing Backend Dependencies
echo ========================================
echo.

REM Check if package.json exists
if not exist package.json (
    echo [ERROR] package.json not found in backend directory
    exit /b 1
)

echo Installing npm packages...
call npm install

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install npm packages
    exit /b 1
)

echo [✓] Backend dependencies installed

REM Check if .env exists
if not exist .env (
    echo.
    echo ========================================
    echo   Creating Environment File
    echo ========================================
    echo.
    
    if exist .env.example (
        copy .env.example .env
        echo [✓] Created .env from .env.example
    ) else (
        echo [WARNING] .env.example not found. Creating basic .env...
        (
            echo PORT=5000
            echo NODE_ENV=development
            echo JWT_SECRET=dev-secret-key-change-in-production
            echo SUPABASE_URL=https://your-supabase-url.supabase.co
            echo SUPABASE_KEY=your-anon-key
            echo SUPABASE_JWT_SECRET=your-jwt-secret
        ) > .env
        echo [✓] Created basic .env file
    )
    
    echo.
    echo [!] Please edit .env and add your Supabase credentials:
    echo    - SUPABASE_URL: Your Supabase project URL
    echo    - SUPABASE_KEY: Your Supabase anon key
    echo    - JWT_SECRET: A secure random string
    echo.
)

echo.
echo ========================================
echo   Backend Setup Complete!
echo ========================================
echo.
echo To start the backend server:
echo   cd backend
echo   npm run dev
echo.
echo To start the Flutter app:
echo   cd zeetech
echo   flutter run
echo.
echo API will be available at: http://localhost:5000
echo Documentation: See MIGRATION_GUIDE.md
echo.

pause
