@echo off
setlocal EnableExtensions
cd /d "%~dp0"

REM A shortcut created from a hidden PowerShell, or PowerShell -WindowStyle Hidden
REM sharing this console, can leave the server running with no window to close.
REM Always continue in a new, visible console.
if /I not "%~1"=="RUN" (
  start "Karaoke Party" /D "%~dp0." cmd.exe /d /c "call "%~f0" RUN"
  exit /b 0
)

title Karaoke Party
REM Own window, minimized: hiding PowerShell in THIS console would hide Karaoke Party too.
start "Acces directe Karaoke" /min /D "%~dp0." powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\make_shortcut.ps1" -RepoRoot "%~dp0." -Target "%~f0"
echo.
echo  Karaoke Party
echo  =============
echo.

call :resolve_python
if errorlevel 1 (
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo [1/4] Creant entorn virtual...
  "%PYTHON_EXE%" -m venv .venv
  if errorlevel 1 (
    echo [ERROR] No s'ha pogut crear el venv.
    pause
    exit /b 1
  )
) else (
  echo [1/4] Entorn virtual OK
)

echo [2/4] Instal·lant el que falti ^(Python, Whisper, stems, ffmpeg, Node.js^)...
echo       La primera vegada pot trigar una estona.
set "PYTHONPATH=%~dp0src"
".venv\Scripts\python.exe" -m karaoke_party.deps
if errorlevel 1 (
  echo [ERROR] No s'han pogut instal·lar les dependències.
  pause
  exit /b 1
)

echo [3/4] Comprovant GPU / CUDA...
where nvidia-smi >nul 2>&1
if errorlevel 1 (
  echo       Sense GPU NVIDIA · Whisper i stems aniran per CPU
) else (
  REM Repair torch CUDA + CUDA 12 libs for Whisper when the driver is present
  REM but the venv still has a CPU wheel or missing cuBLAS 12 DLLs.
  ".venv\Scripts\python.exe" -m karaoke_party.gpu_setup
  if errorlevel 1 (
    echo [ERROR] Hi ha GPU NVIDIA pero no s'ha pogut deixar CUDA a punt.
    echo         Revisa la sortida anterior o prova manualment:
    echo           .venv\Scripts\python.exe -m karaoke_party.gpu_setup
    pause
    exit /b 1
  )
)

echo [4/4] Arrencant servidor a http://127.0.0.1:8765
echo         Tanca aquesta finestra per aturar Karaoke Party.
echo.

REM Always use the venv interpreter (avoid a leftover system Python on PATH).
REM --skip-gpu-setup: the check above already repaired CUDA; avoid a second torch probe.
".venv\Scripts\python.exe" -m karaoke_party --open --host 127.0.0.1 --port 8765 --skip-gpu-setup
set "EXITCODE=%errorlevel%"
echo.
if not "%EXITCODE%"=="0" (
  echo [ERROR] El servidor s'ha aturat amb codi %EXITCODE%.
)
pause
exit /b %EXITCODE%


:resolve_python
set "PYTHON_EXE="
where py >nul 2>&1
if %errorlevel%==0 (
  py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
  if not errorlevel 1 (
    for /f "delims=" %%I in ('py -3 -c "import sys; print(sys.executable)"') do set "PYTHON_EXE=%%I"
  )
)
if not defined PYTHON_EXE (
  where python >nul 2>&1
  if not errorlevel 1 (
    python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
    if not errorlevel 1 (
      for /f "delims=" %%I in ('python -c "import sys; print(sys.executable)"') do set "PYTHON_EXE=%%I"
    )
  )
)
if not defined PYTHON_EXE call :find_installed_python
if defined PYTHON_EXE exit /b 0

echo Python 3.11 o superior no esta instal·lat.
echo Instal·lant Python 3.12...
where winget >nul 2>&1
if errorlevel 1 (
  echo [ERROR] No s'ha trobat winget per instal·lar Python.
  echo         Descarrega'l des de https://www.python.org/downloads/
  echo         i marca "Add python.exe to PATH".
  exit /b 1
)
winget install -e --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements
call :find_installed_python
if defined PYTHON_EXE exit /b 0
echo [ERROR] No s'ha pogut instal·lar Python 3.12.
echo         Descarrega'l des de https://www.python.org/downloads/
echo         i marca "Add python.exe to PATH".
exit /b 1


:find_installed_python
set "PYTHON_EXE="
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
  "%%D\python.exe" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
  if not errorlevel 1 set "PYTHON_EXE=%%D\python.exe"
)
if defined PYTHON_EXE exit /b 0
for /d %%D in ("%ProgramFiles%\Python3*") do (
  "%%D\python.exe" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
  if not errorlevel 1 set "PYTHON_EXE=%%D\python.exe"
)
exit /b 0
