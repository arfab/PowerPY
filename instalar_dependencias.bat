@echo off
title PowerPY - Instalador de Dependencias
echo ===================================================
echo   PowerPY: Instalando dependencias necesarias...
echo ===================================================
echo.
:: Detectar comando de Python disponible
set PYTHON_CMD=
py --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
) else (
    python --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=python
    )
)

if "%PYTHON_CMD%"=="" (
    echo [ERROR] Python no esta instalado en el sistema o no esta en el PATH.
    echo Por favor, instala Python 3.8 o superior y vuelve a intentar.
    echo.
    pause
    exit /b
)

echo [1/2] Actualizando pip...
%PYTHON_CMD% -m pip install --upgrade pip

echo [2/2] Instalando paquetes de requirements.txt...
%PYTHON_CMD% -m pip install -r "%~dp0requirements.txt"

echo.
echo ===================================================
echo   [OK] Dependencias instaladas con exito!
echo   Ya puedes iniciar la app con 'iniciar_app.bat'
echo ===================================================
echo.
pause
