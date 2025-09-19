@echo off
cd /d %~dp0\..
copy "envs\dev.txt" ".env" >nul
".venv\Scripts\python" -m uvicorn app.main:app --reload