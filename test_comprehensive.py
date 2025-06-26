#!/usr/bin/env python3
"""
Script de prueba comprehensivo para evaluar el chatbot CodeHelperNET
con todos los nuevos temas agregados
"""

import sys
import time
from pathlib import Path

def test_chatbot():
    """Ejecutar pruebas comprehensivas del chatbot"""
    
    print("🧪 CodeHelperNET - Pruebas Comprehensivas")
    print("=" * 50)
    
    try:
        from rag_chatbot import RAGChatbot
        
        # Inicializar el chatbot
        print("🤖 Inicializando chatbot...")
        chatbot = RAGChatbot()
        
        # Lista de preguntas de prueba organizadas por categorías
        test_questions = {
            "Fundamentos de .NET": [
                "¿Qué es .NET Core y cuáles son sus características principales?",
                "¿Cuál es la diferencia entre .NET Framework y .NET Core?",
                "¿Qué es el Common Language Runtime (CLR)?"
            ],
            "ASP.NET Core": [
                "¿Cómo funciona el middleware en ASP.NET Core?",
                "¿Qué es la inyección de dependencias en .NET?",
                "¿Cómo configurar el logging en ASP.NET Core?"
            ],
            "Entity Framework": [
                "¿Qué es Entity Framework Core?",
                "¿Cómo usar migrations en EF Core?",
                "¿Cuáles son las mejores prácticas para EF Core?"
            ],
            "Patrones y Arquitectura": [
                "¿Qué es la arquitectura de microservicios?",
                "¿Cómo implementar el patrón Repository?",
                "¿Qué son los patrones de diseño más comunes en .NET?"
            ],
            "Testing y Calidad": [
                "¿Cómo escribir unit tests en .NET?",
                "¿Qué es TDD y cómo aplicarlo?",
                "¿Cuáles son las mejores prácticas de testing?"
            ],
            "DevOps y CI/CD": [
                "¿Cómo configurar CI/CD para aplicaciones .NET?",
                "¿Qué herramientas usar para DevOps en .NET?",
                "¿Cómo hacer deployment de aplicaciones .NET?"
            ],
            "Machine Learning": [
                "¿Cómo usar ML.NET para machine learning?",
                "¿Qué algoritmos están disponibles en ML.NET?",
                "¿Cómo integrar modelos de ML en aplicaciones .NET?"
            ],
            "Desarrollo Cloud": [
                "¿Cómo desplegar aplicaciones .NET en Azure?",
                "¿Qué servicios de Azure son útiles para .NET?",
                "¿Cómo usar Azure DevOps con .NET?"
            ]
        }
        
        # Ejecutar pruebas por categoría
        for category, questions in test_questions.items():
            print(f"\n📚 {category}")
            print("-" * 30)
            
            for i, question in enumerate(questions, 1):
                print(f"\n❓ Pregunta {i}: {question}")
                print("🤖 Respuesta:")
                
                try:
                    response = chatbot.chat(question)
                    print(f"✅ {response}")
                except Exception as e:
                    print(f"❌ Error: {e}")
                
                # Pausa entre preguntas
                time.sleep(2)
        
        print("\n🎉 Pruebas completadas!")
        
    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        return False
    
    return True

def test_specific_topics():
    """Probar temas específicos de los nuevos documentos"""
    
    print("\n🔬 Pruebas de Temas Específicos")
    print("=" * 40)
    
    try:
        from rag_chatbot import RAGChatbot
        chatbot = RAGChatbot()
        
        specific_questions = [
            "¿Qué es la serialización JSON en .NET y cómo usarla?",
            "¿Cómo implementar caching en aplicaciones .NET?",
            "¿Qué es Blazor y cómo funciona?",
            "¿Cómo usar .NET MAUI para desarrollo multiplataforma?",
            "¿Qué son los servicios en segundo plano en .NET?",
            "¿Cómo implementar internacionalización en .NET?",
            "¿Qué estrategias de migración existen para .NET?",
            "¿Cómo optimizar el rendimiento de aplicaciones .NET?"
        ]
        
        for i, question in enumerate(specific_questions, 1):
            print(f"\n🔍 Pregunta {i}: {question}")
            print("🤖 Respuesta:")
            
            try:
                response = chatbot.chat(question)
                print(f"✅ {response}")
            except Exception as e:
                print(f"❌ Error: {e}")
            
            time.sleep(1)
        
        print("\n✅ Pruebas específicas completadas!")
        
    except Exception as e:
        print(f"❌ Error en pruebas específicas: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas comprehensivas del chatbot...")
    
    # Verificar que exista la base vectorial
    vector_db_path = Path("./vector_db")
    if not vector_db_path.exists():
        print("❌ No se encontró la base vectorial. Ejecuta primero:")
        print("   python run_improved_system.py --mode build")
        sys.exit(1)
    
    # Ejecutar pruebas
    if test_chatbot():
        test_specific_topics()
        print("\n🎯 Todas las pruebas completadas exitosamente!")
    else:
        print("\n❌ Las pruebas fallaron")
        sys.exit(1) 