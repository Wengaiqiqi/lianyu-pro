@echo off
setlocal EnableExtensions EnableDelayedExpansion
set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"
set "BACKEND=%ROOT%\backend"
set "FRONTEND=%ROOT%\frontend"

set "DATABASE_URL="
set "DB_MODE=SQLite"
set "DB_SOURCE=default config (backend\app.db)"

call :detect_database

cls
echo ============================================
echo Bookmark System - Startup
echo ============================================
echo.

echo [1/7] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 goto :no_python
echo        Python ... OK
goto :check_node

:no_python
echo [ERROR] Python 3.8+ was not found.
goto :fail

:check_node
echo [2/7] Checking Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 goto :no_node
echo        Node.js ... OK
goto :check_npm

:no_node
echo [ERROR] Node.js 16+ was not found.
goto :fail

:check_npm
echo [3/7] Checking npm...
call npm --version >nul 2>&1
if %errorlevel% neq 0 goto :no_npm
echo        npm ... OK
goto :show_database

:no_npm
echo [ERROR] npm was not found.
goto :fail

:show_database
echo.
echo [4/7] Checking database config...
echo        Database type: !DB_MODE!
echo        Source: !DB_SOURCE!
goto :install_backend

:install_backend
echo.
echo [5/7] Installing backend dependencies...
cd /d "%BACKEND%"
call pip install -r requirements.txt -q 2>&1
if %errorlevel% neq 0 goto :backend_install_failed
echo        Backend dependencies ... OK
goto :install_frontend

:backend_install_failed
echo [ERROR] Backend dependency install failed.
goto :fail

:install_frontend
echo.
echo [6/7] Checking frontend dependencies...
cd /d "%FRONTEND%"
if exist "node_modules\" goto :start_backend
echo        First run detected. Installing frontend dependencies...
call npm install 2>&1
if %errorlevel% neq 0 goto :frontend_install_failed
echo        Frontend dependencies ... OK
goto :start_backend

:frontend_install_failed
echo [ERROR] Frontend dependency install failed.
goto :fail

:start_backend
echo.
echo [7/7] Starting backend and frontend...
cd /d "%BACKEND%"
start "backend" cmd /k python app.py
timeout /t 3 /nobreak >nul

cd /d "%FRONTEND%"
start "frontend" cmd /k npm run dev
timeout /t 3 /nobreak >nul

echo.
echo ============================================
echo Startup completed
echo ============================================
echo.
echo Database: !DB_MODE!
echo Frontend: http://localhost:3000
echo Backend : http://127.0.0.1:5000
echo Admin   : admin / admin123
echo.
pause
exit /b 0

:detect_database
for %%F in ("%ROOT%\.env.local" "%ROOT%\.env" "%BACKEND%\.env.local" "%BACKEND%\.env") do (
    if not defined DATABASE_URL if exist "%%~fF" call :read_env_file "%%~fF"
)

if not defined DATABASE_URL exit /b 0

echo(!DATABASE_URL! | findstr /i /b /c:"mysql+pymysql://" >nul
if not errorlevel 1 (
    set "DB_MODE=MySQL"
    set "DB_SOURCE=!DB_SOURCE! (from DATABASE_URL)"
    exit /b 0
)

echo(!DATABASE_URL! | findstr /i /b /c:"sqlite:///" >nul
if not errorlevel 1 (
    set "DB_MODE=SQLite"
    set "DB_SOURCE=!DB_SOURCE! (from DATABASE_URL)"
    exit /b 0
)

set "DB_MODE=Custom DATABASE_URL"
set "DB_SOURCE=!DB_SOURCE! (from DATABASE_URL)"
exit /b 0

:read_env_file
for /f "usebackq tokens=* delims=" %%L in (%1) do (
    set "LINE=%%L"
    if /i "!LINE:~0,13!"=="DATABASE_URL=" (
        set "DATABASE_URL=!LINE:~13!"
        set "DB_SOURCE=%~1"
    )
)
exit /b 0

:fail
echo.
echo Startup failed. Fix the issue above and try again.
pause
exit /b 1