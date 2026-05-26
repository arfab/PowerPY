@echo off
title PowerPY - BI Dashboard Launcher
echo ===================================================
echo   Iniciando PowerPY BI Dashboard...
echo ===================================================
echo.

:: Comprobar si streamlit esta disponible en Python
python -c "import streamlit" >nul 2>&1
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
python -m streamlit run "%~dp0app.py"
pause
