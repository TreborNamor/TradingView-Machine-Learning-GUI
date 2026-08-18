@echo off
setlocal
set MODE=%1
if "%MODE%"=="" set MODE=local
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0bootstrap.ps1" -Mode %MODE%
endlocal
