@echo off
title AI Recruitment Agent - Terminal Pipeline
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
echo ======================================================================
echo           Starting AI Recruitment Agent Terminal Pipeline...
echo ======================================================================
echo.
cd /d "%~dp0"
py app.py
pause
