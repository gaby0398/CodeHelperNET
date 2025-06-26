@echo off
echo ========================================
echo    CodeHelperNET - Chatbot C# y .NET
echo ========================================
echo.

echo Iniciando CodeHelperNET...
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Por favor instala Python 3.8+ desde https://python.org
    pause
    exit /b 1
)

REM Verificar si Node.js está instalado
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js no está instalado o no está en el PATH
    echo Por favor instala Node.js 18+ desde https://nodejs.org
    pause
    exit /b 1
)

REM Verificar si el entorno virtual existe
if not exist "codehelper_env\Scripts\activate.bat" (
    echo Creando entorno virtual...
    python -m venv codehelper_env
    if errorlevel 1 (
        echo ERROR: No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
)

REM Verificar si las dependencias están instaladas
if not exist "codehelper_env\Lib\site-packages\flask" (
    echo Instalando dependencias de Python...
    call codehelper_env\Scripts\activate.bat
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: No se pudieron instalar las dependencias
        pause
        exit /b 1
    )
)

REM Verificar si la base de datos vectorial existe
if not exist "vector_db" (
    echo Generando base de datos vectorial...
    call codehelper_env\Scripts\activate.bat
    python improved_vector_db.py
    if errorlevel 1 (
        echo ERROR: No se pudo generar la base de datos vectorial
        pause
        exit /b 1
    )
)

REM Verificar si las dependencias del frontend están instaladas
if not exist "frontend\node_modules" (
    echo Instalando dependencias del frontend...
    cd frontend
    npm install
    if errorlevel 1 (
        echo ERROR: No se pudieron instalar las dependencias del frontend
        pause
        exit /b 1
    )
    cd ..
)

echo.
echo ========================================
echo    Iniciando servicios...
echo ========================================
echo.

REM Iniciar el backend en una nueva ventana
echo Iniciando backend (puerto 5000)...
start "CodeHelperNET Backend" cmd /k "call codehelper_env\Scripts\activate.bat && python api_server.py"

REM Esperar un momento para que el backend se inicie
timeout /t 3 /nobreak >nul

REM Iniciar el frontend en una nueva ventana
echo Iniciando frontend (puerto 3000)...
start "CodeHelperNET Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo    Servicios iniciados correctamente
echo ========================================
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Presiona cualquier tecla para abrir el frontend en tu navegador...
pause >nul

REM Abrir el navegador
start http://localhost:3000

echo.
echo ¡CodeHelperNET está listo para usar!
echo.
echo Para detener los servicios, cierra las ventanas de terminal
echo o presiona Ctrl+C en cada una.
echo.
pause 