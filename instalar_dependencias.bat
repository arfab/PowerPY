@echo off
title PowerPY - Instalador de Dependencias
echo ===================================================
echo   PowerPY: Instalando dependencias necesarias...
echo ===================================================
echo.
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado en el sistema o no esta en el PATH.
    echo Por favor, instala Python 3.8 o superior y vuelve a intentar.
    echo.
    pause
    exit /b
)

echo [1/2] Actualizando pip...
python -m pip install --upgrade pip

echo [2/2] Instalando paquetes de requirements.txt...
python -m pip install -r "%~dp0requirements.txt"

echo.
echo ===================================================
echo   [OK] Dependencias instaladas con exito!
echo   Ya puedes iniciar la app con 'iniciar_app.bat'
echo ===================================================
echo.
pause
