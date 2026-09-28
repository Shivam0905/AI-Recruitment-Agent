@echo off
title AI Recruitment Agent - Web Dashboard
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
echo ======================================================================
echo           Starting AI Recruitment Agent Web Dashboard...
echo ======================================================================
echo.
cd /d "%~dp0"
py -m streamlit run web_app.py
pause
