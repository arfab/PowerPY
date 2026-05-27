@echo off
title PowerPY - BI Dashboard Launcher
echo ===================================================
echo   Iniciando PowerPY BI Dashboard...
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

:: Comprobar si streamlit esta disponible en Python
%PYTHON_CMD% -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ALERTA] Streamlit no parece estar instalado. 
    echo Intentando instalar las dependencias primero...
    echo.
    call "%~dp0instalar_dependencias.bat"
)

echo Iniciando servidor local de Streamlit...
echo La aplicacion deberia abrirse automaticamente en tu navegador web.
echo Si no se abre, ve manualmente a: http://localhost:8501
echo.
echo Para apagar el servidor, cierra esta ventana.
echo.
%PYTHON_CMD% -m streamlit run "%~dp0app.py"
pause
