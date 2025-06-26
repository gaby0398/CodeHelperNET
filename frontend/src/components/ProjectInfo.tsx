'use client';

import { Brain, Database, Globe, Zap, BookOpen, Code } from 'lucide-react';

export default function ProjectInfo() {
  const features = [
    {
      icon: <Brain className="w-6 h-6" />,
      title: "IA Especializada",
      description: "Modelo entrenado específicamente en C# y .NET"
    },
    {
      icon: <Database className="w-6 h-6" />,
      title: "Base de Conocimientos",
      description: "76 documentos con información detallada sobre .NET"
    },
    {
      icon: <Globe className="w-6 h-6" />,
      title: "RAG Avanzado",
      description: "Retrieval-Augmented Generation para respuestas precisas"
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Respuestas Rápidas",
      description: "Procesamiento optimizado para respuestas inmediatas"
    },
    {
      icon: <BookOpen className="w-6 h-6" />,
      title: "Contenido Actualizado",
      description: "Información actualizada sobre las últimas versiones de .NET"
    },
    {
      icon: <Code className="w-6 h-6" />,
      title: "Ejemplos Prácticos",
      description: "Código de ejemplo y casos de uso reales"
    }
  ];

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          CodeHelperNET
        </h2>
        <p className="text-gray-600">
          Tu asistente inteligente especializado en C# y .NET
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {features.map((feature, index) => (
          <div
            key={index}
            className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg"
          >
            <div className="text-blue-600 mt-1">
              {feature.icon}
            </div>
            <div>
              <h3 className="font-semibold text-gray-800 text-sm">
                {feature.title}
              </h3>
              <p className="text-xs text-gray-600">
                {feature.description}
              </p>
            </div>
          </div>
        ))}
      </div>

      <div className="border-t pt-4">
        <h3 className="font-semibold text-gray-800 mb-2">
          📚 Temas cubiertos:
        </h3>
        <div className="flex flex-wrap gap-2">
          {[
            "C# Fundamentals",
            "ASP.NET Core",
            "Entity Framework",
            "Design Patterns",
            "Testing",
            "Security",
            "Performance",
            "Cloud Development",
            "Microservices",
            "DevOps"
          ].map((topic, index) => (
            <span
              key={index}
              className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
            >
              {topic}
            </span>
          ))}
        </div>
      </div>

      <div className="mt-4 text-xs text-gray-500 text-center">
        Proyecto universitario de Deep Learning - IF7103 Sistemas Expertos
      </div>
    </div>
  );
} 