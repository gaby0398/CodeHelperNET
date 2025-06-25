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
        self.embedding_model = SentenceTransformer("microsoft/codebert-base-mlm")
        
        # Cross-encoder para re-ranking (mejora la calidad de resultados)
        self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        
        # Modelo LLM para generación (usando un modelo más pequeño pero efectivo)
        self.setup_llm()
        
        # Traductor para respuestas
        self.translator = pipeline("translation_en_to_es", model="Helsinki-NLP/opus-mt-en-es")
        
        # Templates de prompts
        self.setup_prompts()
        
    def setup_llm(self):
        """Configurar modelo LLM para generación"""
        try:
            # Usar un modelo más pequeño pero efectivo para generación
            model_name = "microsoft/DialoGPT-medium"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto" if torch.cuda.is_available() else "cpu"
            )
            self.tokenizer.pad_token = self.tokenizer.eos_token
        except Exception as e:
            print(f"Error cargando modelo LLM: {e}")
            print("Usando modo de solo recuperación...")
            self.model = None
            self.tokenizer = None
    
    def setup_prompts(self):
        """Configurar templates de prompts para diferentes tipos de preguntas"""
        self.prompts = {
            'code_example': PromptTemplate(
                input_variables=["context", "question"],
                template="""Eres un experto en C# y .NET. Basándote en el siguiente contexto, responde la pregunta del usuario.

Contexto:
{context}

Pregunta: {question}

Responde de manera clara y concisa, incluyendo ejemplos de código cuando sea apropiado. Si la información del contexto no es suficiente, indícalo claramente.

Respuesta:"""
            ),
            'concept_explanation': PromptTemplate(
                input_variables=["context", "question"],
                template="""Eres un profesor experto en C# y .NET. Explica el concepto solicitado usando el siguiente contexto como referencia.

Contexto:
{context}

Concepto a explicar: {question}

Proporciona una explicación clara, estructurada y fácil de entender. Incluye ejemplos prácticos cuando sea posible.

Explicación:"""
            ),
            'syntax_help': PromptTemplate(
                input_variables=["context", "question"],
                template="""Eres un asistente de programación especializado en C#. Ayuda con la sintaxis solicitada usando el siguiente contexto.

Contexto:
{context}

Pregunta sobre sintaxis: {question}

Proporciona la sintaxis correcta, ejemplos de uso y explicaciones claras. Incluye casos comunes y mejores prácticas.

Respuesta:"""
            )
        }
    
    def classify_question(self, question: str) -> str:
        """Clasificar el tipo de pregunta para usar el prompt apropiado"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['ejemplo', 'código', 'implementar', 'cómo hacer']):
            return 'code_example'
        elif any(word in question_lower for word in ['qué es', 'explicar', 'concepto', 'definir']):
            return 'concept_explanation'
        elif any(word in question_lower for word in ['sintaxis', 'syntax', 'formato', 'escribir']):
            return 'syntax_help'
        else:
            return 'code_example'  # Default
    
    def retrieve_relevant_chunks(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
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
    
    def generate_response(self, context: str, question: str, question_type: str) -> str:
        """Generar respuesta usando el modelo LLM"""
        if self.model is None:
            return "Lo siento, el modelo de generación no está disponible. Aquí están los fragmentos más relevantes:\n\n" + context
        
        try:
            # Seleccionar prompt apropiado
            prompt_template = self.prompts[question_type]
            prompt = prompt_template.format(context=context, question=question)
            
            # Tokenizar
            inputs = self.tokenizer.encode(prompt, return_tensors="pt", truncation=True, max_length=1024)
            
            # Generar respuesta
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 200,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decodificar respuesta
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extraer solo la parte generada (después del prompt)
            response = response[len(prompt):].strip()
            
            # Limpiar respuesta
            response = re.sub(r'^Respuesta:\s*', '', response)
            response = re.sub(r'^Explicación:\s*', '', response)
            
            return response if response else "No pude generar una respuesta específica con la información disponible."
            
        except Exception as e:
            print(f"Error en generación: {e}")
            return "Error generando respuesta. Aquí están los fragmentos más relevantes:\n\n" + context
    
    def translate_response(self, response: str) -> str:
        """Traducir respuesta al español si es necesario"""
        try:
            # Detectar si ya está en español
            spanish_words = ['es', 'son', 'está', 'están', 'para', 'con', 'por', 'que', 'como', 'cuando']
            if any(word in response.lower() for word in spanish_words):
                return response
            
            # Traducir
            translated = self.translator(response[:500])[0]["translation_text"]
            return translated
        except:
            return response
    
    def chat(self, question: str) -> str:
        """Proceso completo de chat RAG"""
        print(f"🤖 Procesando pregunta: {question}")
        
        # 1. Clasificar pregunta
        question_type = self.classify_question(question)
        print(f"📝 Tipo de pregunta: {question_type}")
        
        # 2. Recuperar contexto relevante
        relevant_chunks = self.retrieve_relevant_chunks(question, n_results=3)
        
        if not relevant_chunks:
            return "❌ No encontré información relevante para tu pregunta. ¿Podrías reformularla?"
        
        # 3. Preparar contexto
        context_parts = []
        for i, chunk in enumerate(relevant_chunks):
            context_parts.append(f"Fragmento {i+1} (Score: {chunk['score']:.3f}):\n{chunk['content']}\n")
        
        context = "\n".join(context_parts)
        
        # 4. Generar respuesta
        print("🧠 Generando respuesta...")
        response = self.generate_response(context, question, question_type)
        
        # 5. Traducir si es necesario
        response = self.translate_response(response)
        
        return response
    
    def interactive_chat(self):
        """Modo interactivo de chat"""
        print("🤖 ChatBot RAG para C# y .NET")
        print("Escribe 'salir' para terminar")
        print("-" * 50)
        
        while True:
            try:
                question = input("\n👤 Tú: ").strip()
                
                if question.lower() in ['salir', 'exit', 'quit']:
                    print("👋 ¡Hasta luego!")
                    break
                
                if not question:
                    continue
                
                # Procesar pregunta
                response = self.chat(question)
                
                print(f"\n🤖 Asistente: {response}")
                
                # Opción para ver contexto
                show_context = input("\n¿Ver contexto usado? (s/n): ").strip().lower()
                if show_context == 's':
                    relevant_chunks = self.retrieve_relevant_chunks(question, n_results=3)
                    print("\n📚 Contexto utilizado:")
                    for i, chunk in enumerate(relevant_chunks):
                        print(f"\n--- Fragmento {i+1} ---")
                        print(f"Tipo: {chunk['metadata']['content_type']}")
                        print(f"Archivo: {chunk['metadata']['filename']}")
                        print(f"Score: {chunk['score']:.3f}")
                        print(f"Contenido: {chunk['content'][:200]}...")
                
            except KeyboardInterrupt:
                print("\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    chatbot = RAGChatbot()
    chatbot.interactive_chat() 