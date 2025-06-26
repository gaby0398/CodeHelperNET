#!/usr/bin/env python3
"""
Script principal para ejecutar el sistema RAG mejorado de CodeHelperNET
"""

import os
import sys
import argparse
from pathlib import Path

def check_dependencies():
    """Verificar que todas las dependencias estén instaladas"""
    required_packages = [
        'sentence_transformers',
        'chromadb', 
        'transformers',
        'torch',
        'langchain',
        'numpy',
        'sklearn'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Faltan las siguientes dependencias:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Instala las dependencias con:")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ Todas las dependencias están instaladas")
    return True

def check_data_files():
    """Verificar que existan archivos de datos"""
    data_dir = Path("./data")
    if not data_dir.exists():
        print("❌ No se encontró el directorio 'data/'")
        return False
    
    txt_files = list(data_dir.glob("*.txt"))
    if not txt_files:
        print("❌ No se encontraron archivos .txt en el directorio 'data/'")
        return False
    
    print(f"✅ Encontrados {len(txt_files)} archivos de datos")
    return True

def build_vector_database():
    """Construir la base de datos vectorial mejorada"""
    print("\n🔨 Construyendo base de datos vectorial mejorada...")
    
    try:
        from improved_vector_db import ImprovedVectorDBGenerator
        
        generator = ImprovedVectorDBGenerator()
        generator.generate_vector_db()
        
        print("✅ Base de datos vectorial construida exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error construyendo la base de datos: {e}")
        return False

def run_chatbot():
    """Ejecutar el chatbot RAG"""
    print("\n🤖 Iniciando ChatBot RAG...")
    
    try:
        from rag_chatbot import RAGChatbot
        
        chatbot = RAGChatbot()
        chatbot.interactive_chat()
        
    except Exception as e:
        print(f"❌ Error ejecutando el chatbot: {e}")
        return False

def run_evaluation():
    """Ejecutar evaluación del sistema"""
    print("\n🔬 Ejecutando evaluación del sistema...")
    
    try:
        from rag_chatbot import RAGChatbot
        from evaluation_metrics import run_evaluation
        
        chatbot = RAGChatbot()
        results = run_evaluation(chatbot)
        
        print("✅ Evaluación completada")
        return True
        
    except Exception as e:
        print(f"❌ Error en la evaluación: {e}")
        return False

def test_single_query(query: str):
    """Probar una consulta individual"""
    print(f"\n🧪 Probando consulta: '{query}'")
    
    try:
        from rag_chatbot import RAGChatbot
        
        chatbot = RAGChatbot()
        response = chatbot.chat(query)
        
        print(f"\n🤖 Respuesta:")
        print(f"{response}")
        
    except Exception as e:
        print(f"❌ Error en la consulta: {e}")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Sistema RAG mejorado para CodeHelperNET")
    parser.add_argument("--mode", choices=["chat", "build", "evaluate", "test"], 
                       default="chat", help="Modo de ejecución")
    parser.add_argument("--query", type=str, help="Consulta para modo test")
    parser.add_argument("--skip-checks", action="store_true", 
                       help="Saltar verificaciones iniciales")
    
    args = parser.parse_args()
    
    print("🚀 CodeHelperNET - Sistema RAG Mejorado")
    print("=" * 50)
    
    # Verificaciones iniciales
    if not args.skip_checks:
        if not check_dependencies():
            sys.exit(1)
        
        if not check_data_files():
            sys.exit(1)
    
    # Ejecutar según el modo
    if args.mode == "build":
        if not build_vector_database():
            sys.exit(1)
        print("\n✅ Sistema listo para usar")
        
    elif args.mode == "chat":
        if not build_vector_database():
            print("❌ No se pudo construir la base de datos")
            sys.exit(1)
        run_chatbot()
        
    elif args.mode == "evaluate":
        if not build_vector_database():
            print("❌ No se pudo construir la base de datos")
            sys.exit(1)
        run_evaluation()
        
    elif args.mode == "test":
        if not args.query:
            print("❌ Debes proporcionar una consulta con --query")
            sys.exit(1)
        
        if not build_vector_database():
            print("❌ No se pudo construir la base de datos")
            sys.exit(1)
        test_single_query(args.query)

if __name__ == "__main__":
    main() 