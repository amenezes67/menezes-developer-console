@echo off
chcp 65001 >nul
cd /d X:\amenezes67\menezes-pro
git switch develop
if errorlevel 1 goto error
git pull --ff-only origin develop
if errorlevel 1 goto error
echo.
echo Repositorio actualizado correctamente.
git status
pause
exit /b 0
:error
echo.
echo ERROR: No se pudo actualizar el repositorio.
pause
exit /b 1
