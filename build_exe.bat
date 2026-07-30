@echo off
setlocal EnableExtensions
cd /d "%~dp0"

title Build Karaoke Party EXE
echo.
echo  Building KaraokeParty.exe ...
echo.

if not exist ".venv\Scripts\python.exe" (
  echo Executa primer KaraokeParty.bat per crear l'entorn.
  pause
  exit /b 1
)

call ".venv\Scripts\activate.bat"
python -m pip install -q --upgrade pip pyinstaller
if errorlevel 1 (
  echo [ERROR] No s'ha pogut instal·lar PyInstaller.
  pause
  exit /b 1
)

pyinstaller --noconfirm --clean --onefile --console ^
  --name KaraokeParty ^
  --paths src ^
  --add-data "web;web" ^
  --hidden-import uvicorn.logging ^
  --hidden-import uvicorn.loops ^
  --hidden-import uvicorn.loops.auto ^
  --hidden-import uvicorn.protocols ^
  --hidden-import uvicorn.protocols.http ^
  --hidden-import uvicorn.protocols.http.auto ^
  --hidden-import uvicorn.protocols.websockets.auto ^
  --hidden-import uvicorn.lifespan ^
  --hidden-import uvicorn.lifespan.on ^
  --collect-all uvicorn ^
  --collect-all fastapi ^
  --collect-all starlette ^
  --collect-all mutagen ^
  --collect-all anyio ^
  --collect-submodules karaoke_party ^
  run_exe.py

if errorlevel 1 (
  echo [ERROR] Ha fallat la compilacio.
  pause
  exit /b 1
)

echo.
echo Built: dist\KaraokeParty.exe
echo Nota: l'EXE inclou el servidor web base. L'alineacio Whisper es mes completa amb KaraokeParty.bat.
echo.
pause
