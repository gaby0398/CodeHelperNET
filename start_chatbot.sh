#!/bin/bash

# Script de inicio rápido para CodeHelperNET
# Este script inicia tanto el backend como el frontend del chatbot

echo "🚀 Iniciando CodeHelperNET Chatbot..."
echo "======================================"

# Verificar si el entorno virtual existe
if [ ! -d "codehelper_env" ]; then
    echo "❌ Error: No se encontró el entorno virtual 'codehelper_env'"
    echo "Por favor, ejecuta primero:"
    echo "  python3 -m venv codehelper_env"
    echo "  source codehelper_env/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Verificar si el frontend existe
if [ ! -d "frontend" ]; then
    echo "❌ Error: No se encontró la carpeta 'frontend'"
    echo "Por favor, asegúrate de que el proyecto esté completo"
    exit 1
fi

# Función para limpiar procesos al salir
cleanup() {
    echo ""
    echo "🛑 Deteniendo servidores..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Servidores detenidos"
    exit 0
}

# Capturar Ctrl+C para limpiar procesos
trap cleanup SIGINT

echo "📦 Iniciando backend (Python/Flask)..."
echo "   Puerto: 5000"
echo "   URL: http://localhost:5000"

# Iniciar backend en segundo plano
source codehelper_env/bin/activate
python api_server.py &
BACKEND_PID=$!

# Esperar un momento para que el backend se inicialice
echo "⏳ Esperando que el backend se inicialice..."
sleep 5

# Verificar si el backend está funcionando
if curl -s http://localhost:5000/health > /dev/null; then
    echo "✅ Backend iniciado correctamente"
else
    echo "❌ Error: No se pudo conectar al backend"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo "🌐 Iniciando frontend (Next.js)..."
echo "   Puerto: 3000"
echo "   URL: http://localhost:3000"

# Iniciar frontend en segundo plano
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Esperar un momento para que el frontend se inicialice
echo "⏳ Esperando que el frontend se inicialice..."
sleep 10

# Verificar si el frontend está funcionando
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend iniciado correctamente"
else
    echo "❌ Error: No se pudo conectar al frontend"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo "🎉 ¡CodeHelperNET está listo!"
echo "================================"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend:  http://localhost:5000"
echo "📊 Health:   http://localhost:5000/health"
echo ""
echo "💡 Ejemplos de preguntas:"
echo "   • ¿Qué es async/await en C#?"
echo "   • ¿Cómo crear una API REST con ASP.NET Core?"
echo "   • ¿Qué son los patrones de diseño?"
echo "   • ¿Cómo implementar Entity Framework Core?"
echo ""
echo "🛑 Presiona Ctrl+C para detener los servidores"
echo ""

# Mantener el script ejecutándose
wait 