@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul 2>&1
echo 正在停止所有服务...
echo.

for /f "tokens=5" %%p in ('netstat -aon 2^>nul ^| findstr ":5000 " ^| findstr "LISTENING"') do (
    taskkill /f /pid %%p >nul 2>&1
)
echo [OK] 后端已停止

for /f "tokens=5" %%p in ('netstat -aon 2^>nul ^| findstr ":3000 " ^| findstr "LISTENING"') do (
    taskkill /f /pid %%p >nul 2>&1
)
echo [OK] 前端已停止

echo.
echo 所有服务已停止
pause
