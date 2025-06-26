#!/usr/bin/env python3
"""
Script de prueba para el chatbot RAG mejorado
"""

from rag_chatbot import RAGChatbot

def test_chatbot():
    """Probar el chatbot con preguntas específicas"""
    print("🧪 Iniciando pruebas del ChatBot RAG mejorado...")
    
    # Inicializar chatbot
    chatbot = RAGChatbot()
    
    # Preguntas de prueba
    test_questions = [
        "¿Qué es ADO.NET?",
        "¿Cómo se conecta a una base de datos en C#?",
        "Muéstrame un ejemplo de SqlConnection",
        "¿Qué es un DataReader?",
        "¿Cómo se usa un DataAdapter?"
    ]
    
    print("\n" + "="*50)
    print("PRUEBAS DEL CHATBOT")
    print("="*50)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🔍 Prueba {i}: {question}")
        print("-" * 40)
        
        try:
            response = chatbot.chat(question)
            print(f"🤖 Respuesta: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 40)
    
    print("\n✅ Pruebas completadas!")
    print("\nPara usar el chatbot interactivo, ejecuta: python rag_chatbot.py")

if __name__ == "__main__":
    test_chatbot() 