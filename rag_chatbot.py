import os
import re
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer, CrossEncoder
from chromadb import PersistentClient
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import numpy as np

class RAGChatbot:
    def __init__(self, db_path: str = "./vector_db"):
        """Inicializar el chatbot RAG completo"""
        self.db_path = db_path
        self.client = PersistentClient(path=db_path)
        
        # Conectar a la colección mejorada
        self.collection = self.client.get_collection("codehelper_csharp_improved")
        
        # Modelo de embeddings para recuperación
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Cross-encoder para re-ranking (mejora la calidad de resultados)
        self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        
        # Modelo LLM para generación (usando un modelo más pequeño pero efectivo)
        self.setup_llm()
        
        # Traductor para respuestas
        self.translator = pipeline("translation_en_to_es", model="Helsinki-NLP/opus-mt-en-es")
        
        # Templates de prompts mejorados
        self.setup_prompts()
        
    def setup_llm(self):
        """Configurar modelo LLM para generación"""
        try:
            # Por ahora, usar solo modo de recuperación para evitar problemas
            print("Usando modo de solo recuperación para mayor estabilidad...")
            self.model = None
            self.tokenizer = None
            return
            
            # Código original comentado para referencia
            # model_name = "microsoft/DialoGPT-small"
            # self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            # self.model = AutoModelForCausalLM.from_pretrained(
            #     model_name,
            #     torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            #     device_map="auto" if torch.cuda.is_available() else "cpu"
            # )
            # 
            # if self.tokenizer.pad_token is None:
            #     self.tokenizer.pad_token = self.tokenizer.eos_token
            # 
            # self.model.config.pad_token_id = self.tokenizer.pad_token_id
            
        except Exception as e:
            print(f"Error cargando modelo LLM: {e}")
            print("Usando modo de solo recuperación...")
            self.model = None
            self.tokenizer = None
    
    def setup_prompts(self):
        """Configurar templates de prompts mejorados para respuestas más limpias"""
        self.prompts = {
            'code_example': PromptTemplate(
                input_variables=["context", "question"],
                template="""Eres un experto en C# y .NET. Responde la pregunta del usuario de manera clara y concisa.

Contexto relevante:
{context}

Pregunta: {question}

Responde de manera directa y útil. Si es necesario, incluye ejemplos de código breves y claros. No agregues información innecesaria.

Respuesta:"""
            ),
            'concept_explanation': PromptTemplate(
                input_variables=["context", "question"],
                template="""Eres un profesor experto en C# y .NET. Explica el concepto solicitado de manera clara y directa.

Contexto relevante:
{context}

Concepto a explicar: {question}

Proporciona una explicación clara, concisa y fácil de entender. Incluye ejemplos prácticos cuando sea útil.

Explicación:"""
            ),
            'syntax_help': PromptTemplate(
                input_variables=["context", "question"],
                template="""Eres un asistente de programación especializado en C#. Ayuda con la sintaxis solicitada.

Contexto relevante:
{context}

Pregunta sobre sintaxis: {question}

Proporciona la sintaxis correcta y ejemplos de uso claros. Sé directo y útil.

Respuesta:"""
            )
        }
    
    def classify_question(self, question: str) -> str:
        """Clasificar el tipo de pregunta para usar el prompt apropiado"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['ejemplo', 'código', 'implementar', 'cómo hacer', 'muestra']):
            return 'code_example'
        elif any(word in question_lower for word in ['qué es', 'explicar', 'concepto', 'definir', 'significa']):
            return 'concept_explanation'
        elif any(word in question_lower for word in ['sintaxis', 'syntax', 'formato', 'escribir', 'declarar']):
            return 'syntax_help'
        else:
            return 'code_example'  # Default
    
    def retrieve_relevant_chunks(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Recuperar chunks relevantes usando embeddings"""
        # Generar embedding de la consulta
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Búsqueda inicial
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results * 2  # Obtener más resultados para re-ranking
        )
        
        # Re-ranking con cross-encoder
        if len(results['documents'][0]) > 0:
            pairs = [[query, doc] for doc in results['documents'][0]]
            scores = self.cross_encoder.predict(pairs)
            
            # Combinar documentos con scores
            doc_scores = list(zip(results['documents'][0], scores, results['metadatas'][0]))
            doc_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Retornar los mejores resultados
            top_results = []
            for doc, score, metadata in doc_scores[:n_results]:
                top_results.append({
                    'content': doc,
                    'score': score,
                    'metadata': metadata
                })
            
            return top_results
        
        return []
    
    def clean_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Limpiar y preparar el contexto para el prompt"""
        context_parts = []
        
        for chunk in chunks:
            # Limpiar el contenido del chunk
            content = chunk['content']
            
            # Remover caracteres extraños y normalizar
            content = re.sub(r'[^\w\s\.\,\;\:\!\?\(\)\[\]\{\}\+\-\*\/\=\<\>\"\'\n\r\t]', '', content)
            content = re.sub(r'\s+', ' ', content)
            content = content.strip()
            
            # Solo agregar si el contenido es relevante (score > 0.5)
            if chunk['score'] > 0.5 and len(content) > 20:
                context_parts.append(content)
        
        return "\n\n".join(context_parts)
    
    def generate_response(self, context: str, question: str, question_type: str) -> str:
        """Generar respuesta usando el modelo LLM o modo de recuperación"""
        if self.model is None:
            # Modo de solo recuperación - proporcionar respuestas estructuradas
            if not context:
                return "No encontré información específica para tu pregunta. ¿Podrías reformularla o ser más específico?"
            
            # Crear respuesta estructurada basada en el contexto
            if question_type == 'concept_explanation':
                # Para explicaciones de conceptos
                return f"Basándome en la información disponible:\n\n{context[:600]}..."
            elif question_type == 'code_example':
                # Para ejemplos de código
                return f"Aquí tienes información relevante con ejemplos:\n\n{context[:600]}..."
            elif question_type == 'syntax_help':
                # Para ayuda de sintaxis
                return f"Información sobre sintaxis:\n\n{context[:600]}..."
            else:
                # Respuesta general
                return f"Información relevante:\n\n{context[:600]}..."
        
        try:
            # Seleccionar prompt apropiado
            prompt_template = self.prompts[question_type]
            prompt = prompt_template.format(context=context, question=question)
            
            # Tokenizar con attention mask explícito
            inputs = self.tokenizer(
                prompt, 
                return_tensors="pt", 
                truncation=True, 
                max_length=1024,
                padding=True,
                return_attention_mask=True
            )
            
            # Generar respuesta
            with torch.no_grad():
                outputs = self.model.generate(
                    input_ids=inputs['input_ids'],
                    attention_mask=inputs['attention_mask'],
                    max_length=inputs['input_ids'].shape[1] + 100,  # Respuestas más cortas
                    temperature=0.7,  # Balance entre creatividad y precisión
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1,  # Evitar repeticiones
                    no_repeat_ngram_size=3   # Evitar repetición de frases
                )
            
            # Decodificar respuesta
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extraer solo la parte generada (después del prompt)
            response = response[len(prompt):].strip()
            
            # Limpiar respuesta
            response = re.sub(r'^Respuesta:\s*', '', response)
            response = re.sub(r'^Explicación:\s*', '', response)
            response = re.sub(r'\n+', '\n', response)  # Normalizar saltos de línea
            
            # Si la respuesta está vacía o es muy corta, usar fallback
            if not response or len(response) < 20:
                if context:
                    return f"Basándome en la información disponible:\n\n{context[:300]}..."
                else:
                    return "No pude generar una respuesta específica. ¿Podrías reformular tu pregunta?"
            
            return response
            
        except Exception as e:
            print(f"Error en generación: {e}")
            if context:
                return f"Basándome en la información disponible:\n\n{context[:300]}..."
            else:
                return "Error generando respuesta. ¿Podrías reformular tu pregunta?"
    
    def translate_response(self, response: str) -> str:
        """Traducir respuesta al español si es necesario"""
        try:
            # Detectar si ya está en español
            spanish_words = ['es', 'son', 'está', 'están', 'para', 'con', 'por', 'que', 'como', 'cuando', 'una', 'las', 'los']
            spanish_count = sum(1 for word in spanish_words if word in response.lower())
            
            if spanish_count >= 2:  # Si tiene al menos 2 palabras en español
                return response
            
            # Traducir solo si es necesario
            translated = self.translator(response[:400])[0]["translation_text"]
            return translated
        except:
            return response
    
    def chat(self, question: str) -> str:
        """Proceso completo de chat RAG - versión limpia"""
        # 1. Clasificar pregunta
        question_type = self.classify_question(question)
        
        # 2. Recuperar contexto relevante
        relevant_chunks = self.retrieve_relevant_chunks(question, n_results=2)
        
        if not relevant_chunks:
            return "No encontré información relevante para tu pregunta. ¿Podrías reformularla o ser más específico?"
        
        # 3. Preparar contexto limpio
        context = self.clean_context(relevant_chunks)
        
        if not context:
            return "No encontré información útil en la base de datos. ¿Podrías reformular tu pregunta?"
        
        # 4. Generar respuesta
        response = self.generate_response(context, question, question_type)
        
        # 5. Traducir si es necesario
        response = self.translate_response(response)
        
        return response
    
    def interactive_chat(self):
        """Modo interactivo de chat - versión limpia"""
        print("🤖 ChatBot RAG para C# y .NET")
        print("Escribe 'salir' para terminar")
        print("-" * 40)
        
        while True:
            try:
                question = input("\n👤 Tú: ").strip()
                
                if question.lower() in ['salir', 'exit', 'quit']:
                    print("👋 ¡Hasta luego!")
                    break
                
                if not question:
                    continue
                
                # Procesar pregunta y mostrar respuesta limpia
                response = self.chat(question)
                print(f"\n🤖 {response}")
                
            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    chatbot = RAGChatbot()
    chatbot.interactive_chat() 