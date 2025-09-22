@echo off
where code >nul 2>nul
if errorlevel 1 (
    echo VS Code is not installed or 'code' is not in your PATH.
    pause
    exit /b
)
code "C:\Users\ESOS Dev\Desktop\FastApi-project-initializer\generated"