@echo off
chcp 65001 >nul
title Menezes GitHub Manager v3.0
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 github-manager.py
) else (
    python github-manager.py
)

if errorlevel 1 (
    echo.
    echo No fue posible ejecutar el administrador.
    echo Verifique que Python 3 este instalado.
    pause
)
