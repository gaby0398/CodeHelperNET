import os
import re
import json
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
from chromadb.config import Settings
import numpy as np

class ImprovedVectorDBGenerator:
    def __init__(self, db_path: str = "./vector_db"):
        """Inicializar el generador de base vectorial mejorado"""
        self.db_path = db_path
        self.client = PersistentClient(path=db_path)
        
        # Usar modelo especializado para código (mejor que el multilingüe genérico)
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Crear colección con metadatos
        self.collection = self.client.get_or_create_collection(
            name="codehelper_csharp_improved",
            metadata={"description": "Base de datos vectorial para C# y .NET"}
        )
    
    def split_text_semantic(self, text: str, max_length: int = 500) -> List[str]:
        """División semántica mejorada del texto"""
        chunks = []
        
        # Dividir por secciones principales (títulos con #)
        sections = re.split(r'\n(?=#+\s)', text)
        
        for section in sections:
            if not section.strip():
                continue
                
            # Si la sección es pequeña, agregarla completa
            if len(section) <= max_length:
                chunks.append(section.strip())
                continue
            
            # Dividir secciones grandes por párrafos
            paragraphs = re.split(r'\n\s*\n', section)
            current_chunk = ""
            
            for paragraph in paragraphs:
                if len(current_chunk) + len(paragraph) <= max_length:
                    current_chunk += paragraph + "\n\n"
                else:
                    if current_chunk.strip():
                        chunks.append(current_chunk.strip())
                    current_chunk = paragraph + "\n\n"
            
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
        
        return chunks
    
    def classify_content(self, text: str) -> str:
        """Clasificar el tipo de contenido"""
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in ['using ', 'import ', 'namespace ']):
            return "import_statement"
        elif any(keyword in text_lower for keyword in ['class ', 'public class', 'private class']):
            return "class_definition"
        elif any(keyword in text_lower for keyword in ['public ', 'private ', 'static ', 'async ', 'void ', 'int ', 'string ', 'bool ']) and '(' in text and ')' in text:
            return "method_definition"
        elif any(keyword in text_lower for keyword in ['sqlconnection', 'sqldataadapter', 'sqldatareader', 'execute', 'query', 'database']):
            return "database_operation"
        elif any(keyword in text_lower for keyword in ['ado.net', 'entity framework', 'linq', 'asp.net']):
            return "framework_concept"
        else:
            return "general_concept"
    
    def process_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Procesar un archivo y generar chunks con metadatos"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Dividir el contenido semánticamente
            chunks = self.split_text_semantic(content)
            
            documents = []
            for i, chunk in enumerate(chunks):
                if len(chunk.strip()) < 50:  # Ignorar chunks muy pequeños
                    continue
                
                # Clasificar el contenido
                content_type = self.classify_content(chunk)
                
                # Extraer título o primera línea como descripción
                lines = chunk.split('\n')
                title = lines[0].strip() if lines else "Sin título"
                if title.startswith('#'):
                    title = title.lstrip('#').strip()
                
                document = {
                    "id": f"{os.path.basename(file_path)}_{i}",
                    "text": chunk,
                    "metadata": {
                        "file": os.path.basename(file_path),
                        "content_type": content_type,
                        "title": title[:100],  # Limitar longitud del título
                        "chunk_index": i,
                        "length": len(chunk)
                    }
                }
                documents.append(document)
            
            return documents
            
        except Exception as e:
            print(f"Error procesando {file_path}: {e}")
            return []
    
    def generate_vector_db(self):
        """Generar la base de datos vectorial completa"""
        print("🚀 Iniciando generación de base vectorial mejorada...")
        
        # Limpiar colección existente
        try:
            self.client.delete_collection("codehelper_csharp_improved")
            self.collection = self.client.create_collection(
                name="codehelper_csharp_improved",
                metadata={"description": "Base de datos vectorial para C# y .NET"}
            )
        except:
            pass
        
        # Procesar archivos en el directorio data
        data_dir = "./data"
        all_documents = []
        
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.endswith('.txt'):
                    file_path = os.path.join(data_dir, filename)
                    print(f"Procesando: {file_path}")
                    
                    documents = self.process_file(file_path)
                    all_documents.extend(documents)
        
        if not all_documents:
            print("❌ No se encontraron documentos para procesar")
            return
        
        # Preparar datos para ChromaDB
        ids = [doc["id"] for doc in all_documents]
        texts = [doc["text"] for doc in all_documents]
        metadatas = [doc["metadata"] for doc in all_documents]
        
        # Generar embeddings y agregar a la base de datos
        print(f"📝 Agregando {len(all_documents)} chunks a la base vectorial...")
        
        # Agregar en lotes para mejor rendimiento
        batch_size = 10
        for i in range(0, len(all_documents), batch_size):
            batch_ids = ids[i:i+batch_size]
            batch_texts = texts[i:i+batch_size]
            batch_metadatas = metadatas[i:i+batch_size]
            
            self.collection.add(
                ids=batch_ids,
                documents=batch_texts,
                metadatas=batch_metadatas
            )
        
        # Estadísticas finales
        print(f"✅ Base vectorial mejorada creada con {len(all_documents)} chunks")
        
        # Mostrar estadísticas por tipo de contenido
        content_types = {}
        for doc in all_documents:
            content_type = doc["metadata"]["content_type"]
            content_types[content_type] = content_types.get(content_type, 0) + 1
        
        print("📊 Estadísticas de la colección:")
        print(f"   - Total de documentos: {len(all_documents)}")
        print(f"   - Distribución por tipo:")
        for content_type, count in content_types.items():
            print(f"     * {content_type}: {count}")

if __name__ == "__main__":
    generator = ImprovedVectorDBGenerator()
    generator.generate_vector_db() 