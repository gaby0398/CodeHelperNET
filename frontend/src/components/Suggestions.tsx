'use client';

import { Code, BookOpen, Database, Rocket, Shield, Cloud } from 'lucide-react';

interface SuggestionsProps {
  onSuggestionClick: (suggestion: string) => void;
}

const suggestions = [
  {
    icon: <Code className="w-5 h-5" />,
    text: "¿Cómo implementar async/await en C#?",
    category: "Programación"
  },
  {
    icon: <Database className="w-5 h-5" />,
    text: "¿Qué es Entity Framework Core?",
    category: "Base de Datos"
  },
  {
    icon: <Rocket className="w-5 h-5" />,
    text: "¿Cómo crear una API REST con ASP.NET Core?",
    category: "Web Development"
  },
  {
    icon: <Shield className="w-5 h-5" />,
    text: "¿Cuáles son las mejores prácticas de seguridad en .NET?",
    category: "Seguridad"
  },
  {
    icon: <Cloud className="w-5 h-5" />,
    text: "¿Cómo desplegar una aplicación .NET en Azure?",
    category: "Cloud"
  },
  {
    icon: <BookOpen className="w-5 h-5" />,
    text: "¿Qué son los patrones de diseño más comunes en C#?",
    category: "Arquitectura"
  }
];

export default function Suggestions({ onSuggestionClick }: SuggestionsProps) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">
        💡 Preguntas sugeridas
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {suggestions.map((suggestion, index) => (
          <button
            key={index}
            onClick={() => onSuggestionClick(suggestion.text)}
            className="flex items-center space-x-3 p-3 text-left bg-gray-50 hover:bg-blue-50 border border-gray-200 hover:border-blue-300 rounded-lg transition-all duration-200 group"
          >
            <div className="text-gray-600 group-hover:text-blue-600 transition-colors">
              {suggestion.icon}
            </div>
            <div className="flex-1">
              <div className="text-sm font-medium text-gray-800 group-hover:text-blue-800">
                {suggestion.text}
              </div>
              <div className="text-xs text-gray-500">
                {suggestion.category}
              </div>
            </div>
          </button>
        ))}
      </div>
      <div className="mt-4 text-xs text-gray-500 text-center">
        Haz clic en cualquier sugerencia para empezar a chatear
      </div>
    </div>
  );
} 