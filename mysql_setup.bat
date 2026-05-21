@echo off
setlocal EnableExtensions
set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"
cd /d "%ROOT%"

echo ============================================
echo MySQL setup launcher
echo ============================================
echo.
echo Interactive text is shown in Chinese inside mysql_setup.py.
echo.

python mysql_setup.py %*
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] MySQL setup did not complete.
) else (
    echo.
    echo [DONE] MySQL setup finished.
)

echo.
pause