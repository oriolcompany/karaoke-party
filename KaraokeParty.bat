@echo off
setlocal EnableExtensions
cd /d "%~dp0"

title Karaoke Party
echo.
echo  Karaoke Party
echo  =============
echo.

where py >nul 2>&1
if %errorlevel%==0 (
  set "PYTHON=py -3"
) else (
  where python >nul 2>&1
  if errorlevel 1 (
    echo [ERROR] Cal Python 3.11 o superior instal·lat i al PATH.
    echo Descarrega'l des de https://www.python.org/downloads/
    pause
    exit /b 1
  )
  set "PYTHON=python"
)

if not exist ".venv\Scripts\python.exe" (
  echo [1/3] Creant entorn virtual...
  %PYTHON% -m venv .venv
  if errorlevel 1 (
    echo [ERROR] No s'ha pogut crear el venv.
    pause
    exit /b 1
  )
) else (
  echo [1/3] Entorn virtual OK
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 (
  echo [ERROR] No s'ha pogut activar el venv.
  pause
  exit /b 1
)

echo [2/3] Comprovant dependències...
python -c "import fastapi, uvicorn, mutagen, httpx" 1>nul 2>nul
if errorlevel 1 (
  echo       Instal·lant paquet base...
  python -m pip install -q --upgrade pip
  pip install -q -e .
  if errorlevel 1 (
    echo [ERROR] No s'han pogut instal·lar les dependències basiques.
    pause
    exit /b 1
  )
) else (
  echo       Paquet base OK
)

python -c "import faster_whisper" 1>nul 2>nul
if errorlevel 1 (
  echo       Instal·lant Whisper ^(alineacio^)...
  pip install -q "faster-whisper>=1.0.0"
  if errorlevel 1 (
    echo [AVIS] No s'ha pogut instal·lar Whisper. Continuo sense alineacio avançada.
  ) else (
    echo       Whisper OK
  )
) else (
  echo       Whisper OK
)

echo [3/3] Arrencant servidor a http://127.0.0.1:8765
echo         Tanca aquesta finestra per aturar Karaoke Party.
echo.

REM Use python -m so we don't depend on karaoke-party.exe (often locked if already running).
python -m karaoke_party --open --host 127.0.0.1 --port 8765
set "EXITCODE=%errorlevel%"
echo.
if not "%EXITCODE%"=="0" (
  echo [ERROR] El servidor s'ha aturat amb codi %EXITCODE%.
)
pause
exit /b %EXITCODE%
