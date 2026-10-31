@echo off
title King Animated Desktop
cd /d "%~dp0"
python -m pip install --quiet -r requirements.txt
if errorlevel 1 (
  echo Python not found or pip failed. Install Python 3.9+ from python.org and tick "Add Python to PATH".
  pause & exit /b 1
)
python run.py --settings
