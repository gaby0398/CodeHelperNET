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
        self.embedding_model = SentenceTransformer("microsoft/codebert-base-mlm")
        
        # Crear colección con metadatos
        self.collection = self.client.get_or_create_collection(
            name="codehelper_csharp_improved",
            metadata={"description": "Base de datos vectorial mejorada para C# y .NET"}
        )
        
    def clean_text(self, text: str) -> str:
        """Limpiar texto de errores de OCR y caracteres extraños"""
        # Remover caracteres extraños comunes en OCR
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\(\)\[\]\{\}\+\-\*\/\=\<\>\"\'\n\r\t]', '', text)
        # Normalizar espacios
        text = re.sub(r'\s+', ' ', text)
        # Remover líneas vacías múltiples
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()
    
    def semantic_chunking(self, text: str, max_length: int = 512) -> List[Dict[str, Any]]:
        """
        Chunking semántico que preserva contexto y estructura
        """
        chunks = []
        
        # Dividir por secciones principales
        sections = re.split(r'\n(?=[A-Z][A-Z\s]+:?\n)', text)
        
        for section in sections:
            if len(section.strip()) < 50:  # Ignorar secciones muy pequeñas
                continue
                
            # Detectar tipo de contenido
            content_type = self.detect_content_type(section)
            
            # Dividir sección en chunks más pequeños si es necesario
            if len(section) > max_length:
                sub_chunks = self.split_large_section(section, max_length)
                for i, chunk in enumerate(sub_chunks):
                    chunks.append({
                        'content': chunk,
                        'type': content_type,
                        'section': section[:100] + "..." if len(section) > 100 else section,
                        'chunk_id': i
                    })
            else:
                chunks.append({
                    'content': section,
                    'type': content_type,
                    'section': section[:100] + "..." if len(section) > 100 else section,
                    'chunk_id': 0
                })
        
        return chunks
    
    def detect_content_type(self, text: str) -> str:
        """Detectar tipo de contenido basado en patrones"""
        text_lower = text.lower()
        
        if re.search(r'(class|interface|struct|enum)\s+\w+', text):
            return 'class_definition'
        elif re.search(r'(public|private|protected)\s+(static\s+)?(void|int|string|bool|double)', text):
            return 'method_definition'
        elif re.search(r'(if|for|while|foreach|switch)\s*\(', text):
            return 'control_structure'
        elif re.search(r'(using|namespace|import)', text):
            return 'import_statement'
        elif re.search(r'(console\.writeline|console\.readline)', text):
            return 'console_io'
        elif re.search(r'(sql|select|insert|update|delete)', text):
            return 'database_operation'
        elif re.search(r'(xml|json|serialization)', text):
            return 'data_format'
        else:
            return 'general_concept'
    
    def split_large_section(self, section: str, max_length: int) -> List[str]:
        """Dividir secciones grandes preservando contexto"""
        chunks = []
        current_chunk = ""
        
        # Dividir por líneas para preservar estructura
        lines = section.split('\n')
        
        for line in lines:
            if len(current_chunk) + len(line) < max_length:
                current_chunk += line + '\n'
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = line + '\n'
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generar embeddings usando el modelo especializado"""
        embeddings = self.embedding_model.encode(texts, convert_to_tensor=True)
        return embeddings.cpu().numpy().tolist()
    
    def process_file(self, filepath: str) -> List[Dict[str, Any]]:
        """Procesar un archivo completo"""
        print(f"Procesando: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Limpiar contenido
        cleaned_content = self.clean_text(content)
        
        # Chunking semántico
        chunks = self.semantic_chunking(cleaned_content)
        
        # Agregar metadatos del archivo
        filename = os.path.basename(filepath)
        for chunk in chunks:
            chunk['filename'] = filename
            chunk['filepath'] = filepath
        
        return chunks
    
    def build_vector_db(self, data_dir: str = "./data"):
        """Construir la base de datos vectorial completa"""
        all_chunks = []
        doc_id = 0
        
        # Procesar todos los archivos
        for filename in os.listdir(data_dir):
            if filename.endswith(".txt") and "Index" not in filename:
                filepath = os.path.join(data_dir, filename)
                try:
                    chunks = self.process_file(filepath)
                    all_chunks.extend(chunks)
                except Exception as e:
                    print(f"Error procesando {filename}: {e}")
        
        print(f"Total de chunks generados: {len(all_chunks)}")
        
        # Generar embeddings en lotes para eficiencia
        batch_size = 32
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i:i + batch_size]
            
            # Preparar datos para ChromaDB
            documents = [chunk['content'] for chunk in batch]
            embeddings = self.generate_embeddings(documents)
            ids = [f"chunk_{doc_id + j}" for j in range(len(batch))]
            
            # Metadatos enriquecidos
            metadatas = []
            for chunk in batch:
                metadata = {
                    'content_type': chunk['type'],
                    'filename': chunk['filename'],
                    'section': chunk['section'],
                    'chunk_id': chunk['chunk_id'],
                    'length': len(chunk['content'])
                }
                metadatas.append(metadata)
            
            # Agregar a la colección
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            doc_id += len(batch)
            print(f"Procesados {doc_id}/{len(all_chunks)} chunks")
        
        print(f"✅ Base vectorial mejorada creada con {doc_id} chunks")
        print(f"📊 Estadísticas de la colección:")
        print(f"   - Total de documentos: {self.collection.count()}")
        
        # Mostrar estadísticas por tipo de contenido
        results = self.collection.get()
        content_types = {}
        for metadata in results['metadatas']:
            content_type = metadata['content_type']
            content_types[content_type] = content_types.get(content_type, 0) + 1
        
        print("   - Distribución por tipo:")
        for content_type, count in content_types.items():
            print(f"     * {content_type}: {count}")

if __name__ == "__main__":
    generator = ImprovedVectorDBGenerator()
    generator.build_vector_db() 