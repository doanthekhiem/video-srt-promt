@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8

where py >nul 2>&1 && set PY=py -3
if not defined PY where python >nul 2>&1 && set PY=python
if not defined PY (
  echo Khong tim thay Python. Cai Python 3 roi chay lai.
  pause
  exit /b 1
)

echo Khoi dong server tai http://127.0.0.1:8765/
echo Dong cua so nay de dung server.
echo.
%PY% split_video.py
pause
