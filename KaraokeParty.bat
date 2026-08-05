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
  echo [1/4] Creant entorn virtual...
  %PYTHON% -m venv .venv
  if errorlevel 1 (
    echo [ERROR] No s'ha pogut crear el venv.
    pause
    exit /b 1
  )
) else (
  echo [1/4] Entorn virtual OK
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 (
  echo [ERROR] No s'ha pogut activar el venv.
  pause
  exit /b 1
)

echo [2/4] Comprovant dependències Python...
python -c "import fastapi, uvicorn, mutagen, httpx, multipart" 1>nul 2>nul
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
  pip install -q -e ".[align]"
  if errorlevel 1 (
    echo [ERROR] No s'ha pogut instal·lar Whisper ^(faster-whisper^).
    pause
    exit /b 1
  )
) else (
  echo       Whisper OK
)

python -c "import importlib.util,sys; sys.exit(0 if importlib.util.find_spec('audio_separator') else 1)" 1>nul 2>nul
if errorlevel 1 (
  echo       Instal·lant separacio de pistes ^(stems^)...
  where nvidia-smi >nul 2>&1
  if errorlevel 1 (
    pip install -q -e ".[stems-cpu]"
  ) else (
    pip install -q -e ".[stems]"
    if errorlevel 1 (
      echo       GPU fallida · provant stems-cpu...
      pip install -q -e ".[stems-cpu]"
    )
  )
  if errorlevel 1 (
    echo [ERROR] No s'ha pogut instal·lar audio-separator.
    echo         Prova manualment: pip install -e ".[stems]"  o  ".[stems-cpu]"
    pause
    exit /b 1
  )
) else (
  echo       Stems OK
)

echo [3/4] Comprovant ffmpeg...
where ffmpeg >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Cal ffmpeg al PATH per generar pistes instrumental/veu.
  echo         Descarrega'l des de https://ffmpeg.org/download.html
  echo         i reinicia la consola despres d'afegir-lo al PATH.
  pause
  exit /b 1
) else (
  echo       ffmpeg OK
)

echo [4/4] Arrencant servidor a http://127.0.0.1:8765
echo         Tanca aquesta finestra per aturar Karaoke Party.
echo.

REM Always use the venv interpreter (avoid a leftover system Python on PATH).
".venv\Scripts\python.exe" -m karaoke_party --open --host 127.0.0.1 --port 8765
set "EXITCODE=%errorlevel%"
echo.
if not "%EXITCODE%"=="0" (
  echo [ERROR] El servidor s'ha aturat amb codi %EXITCODE%.
)
pause
exit /b %EXITCODE%
