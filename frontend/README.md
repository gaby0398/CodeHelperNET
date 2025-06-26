# CodeHelperNET Frontend

Frontend moderno para el chatbot especializado en C# y .NET, desarrollado con Next.js y TypeScript.

## 🚀 Características

- **Interfaz moderna y responsiva** con Tailwind CSS
- **Chat en tiempo real** con el backend de Python
- **Sugerencias de preguntas** para facilitar el uso
- **Información del proyecto** y capacidades
- **Diseño adaptativo** para móviles y escritorio
- **Iconos intuitivos** con Lucide React

## 🛠️ Tecnologías

- **Next.js 14** - Framework de React
- **TypeScript** - Tipado estático
- **Tailwind CSS** - Framework de CSS
- **Lucide React** - Iconos
- **React Hooks** - Estado y efectos

## 📦 Instalación

1. **Clonar el repositorio** (si no lo has hecho ya):
```bash
git clone <tu-repositorio>
cd CodeHelperNET/frontend
```

2. **Instalar dependencias**:
```bash
npm install
```

3. **Configurar variables de entorno**:
Crea un archivo `.env.local` en la raíz del frontend:
```env
# URL del backend de Python
PYTHON_BACKEND_URL=http://localhost:5000

# URL de la API del frontend (para desarrollo local)
NEXT_PUBLIC_API_URL=/api
```

## 🚀 Desarrollo

1. **Iniciar el servidor de desarrollo**:
```bash
npm run dev
```

2. **Abrir en el navegador**:
```
http://localhost:3000
```

## 🔧 Configuración

### Variables de Entorno

- `PYTHON_BACKEND_URL`: URL del backend de Python (por defecto: http://localhost:5000)
- `NEXT_PUBLIC_API_URL`: URL de la API del frontend (por defecto: /api)

### Estructura del Proyecto

```
frontend/
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   └── chat/
│   │   │       └── route.ts          # API route para chat
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx                  # Página principal
│   ├── components/
│   │   ├── ChatInterface.tsx         # Componente principal del chat
│   │   ├── Suggestions.tsx           # Sugerencias de preguntas
│   │   └── ProjectInfo.tsx           # Información del proyecto
│   └── services/
│       └── chatService.ts            # Servicio para comunicación con API
├── public/
├── next.config.js                    # Configuración de Next.js
└── package.json
```

## 🌐 Despliegue en Vercel

1. **Conectar con GitHub**:
   - Sube tu código a GitHub
   - Conecta tu repositorio con Vercel

2. **Configurar variables de entorno en Vercel**:
   - `PYTHON_BACKEND_URL`: URL de tu backend desplegado
   - `NEXT_PUBLIC_API_URL`: /api (para Vercel)

3. **Desplegar**:
   - Vercel detectará automáticamente que es un proyecto Next.js
   - El despliegue se hará automáticamente en cada push

## 🔗 Integración con Backend

El frontend se comunica con el backend de Python a través de la API route `/api/chat`. Asegúrate de que:

1. **El backend esté ejecutándose** en la URL especificada
2. **El endpoint `/chat` esté disponible** en el backend
3. **CORS esté configurado** correctamente en el backend

### Formato de la API

**Request**:
```json
{
  "message": "¿Qué es async/await en C#?"
}
```

**Response**:
```json
{
  "response": "async/await es un patrón de programación asíncrona en C#..."
}
```

## 🎨 Personalización

### Colores y Temas

Los colores principales están definidos en Tailwind CSS:
- **Azul**: `blue-600`, `blue-700` (botones y elementos principales)
- **Púrpura**: `purple-600` (gradientes y acentos)
- **Gris**: `gray-50`, `gray-100`, `gray-800` (fondos y texto)

### Componentes

Puedes personalizar los componentes editando:
- `ChatInterface.tsx` - Interfaz principal del chat
- `Suggestions.tsx` - Sugerencias de preguntas
- `ProjectInfo.tsx` - Información del proyecto

## 🐛 Solución de Problemas

### Error de Conexión con Backend

1. Verifica que el backend esté ejecutándose
2. Confirma la URL en las variables de entorno
3. Revisa los logs del backend para errores

### Error de CORS

1. Asegúrate de que el backend permita requests desde el frontend
2. Verifica la configuración de CORS en el backend

### Error de Build

1. Verifica que todas las dependencias estén instaladas
2. Revisa los errores de TypeScript
3. Asegúrate de que todos los imports sean correctos

## 📝 Scripts Disponibles

- `npm run dev` - Servidor de desarrollo
- `npm run build` - Build de producción
- `npm run start` - Servidor de producción
- `npm run lint` - Linting del código

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.
