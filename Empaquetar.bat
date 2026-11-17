@echo off
setlocal EnableExtensions
cd /d "%~dp0"

title Empaquetar Karaoke Party
echo.
echo  Empaquetar Karaoke Party
echo  ========================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\empaquetar.ps1"
set "EXITCODE=%errorlevel%"
echo.
if not "%EXITCODE%"=="0" (
  echo [ERROR] No s'ha pogut crear el paquet. Codi %EXITCODE%.
) else (
  echo Paquet creat. El pots enviar tal qual.
)
echo.
pause
exit /b %EXITCODE%
