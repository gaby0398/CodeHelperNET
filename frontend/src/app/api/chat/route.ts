import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { message } = await request.json();

    if (!message) {
      return NextResponse.json(
        { error: 'Mensaje requerido' },
        { status: 400 }
      );
    }

    // URL del backend de Python (ajusta según tu configuración)
    const pythonBackendUrl = process.env.PYTHON_BACKEND_URL || 'http://localhost:5000';
    
    const response = await fetch(`${pythonBackendUrl}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error(`Error del backend: ${response.status}`);
    }

    const data = await response.json();
    
    return NextResponse.json({ 
      response: data.response || data.message || 'No se recibió respuesta del servidor'
    });

  } catch (error) {
    console.error('Error en la API route:', error);
    
    return NextResponse.json(
      { 
        error: 'Error interno del servidor',
        details: error instanceof Error ? error.message : 'Error desconocido'
      },
      { status: 500 }
    );
  }
} 