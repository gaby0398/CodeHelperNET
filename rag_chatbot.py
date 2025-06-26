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
                template="""Eres un experto en C# y .NET. El usuario está pidiendo un ejemplo de código. Proporciona una respuesta clara y útil.

Contexto relevante:
{context}

Pregunta del usuario: {question}

Responde de manera directa y útil. Si hay ejemplos de código en el contexto, preséntalos de forma clara. Si no hay ejemplos específicos, proporciona información útil sobre el tema.

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
            ),
            'general_help': PromptTemplate(
                input_variables=["context", "question"],
                template="""Eres un asistente experto en C# y .NET. Responde la pregunta del usuario de manera útil y clara.

Contexto relevante:
{context}

Pregunta: {question}

Proporciona una respuesta directa y útil. Si hay información relevante en el contexto, úsala. Si no, proporciona información general útil sobre C# y .NET.

Respuesta:"""
            )
        }
    
    def classify_question(self, question: str) -> str:
        """Clasificar el tipo de pregunta para usar el prompt apropiado - MEJORADO"""
        question_lower = question.lower()
        
        # Palabras clave para ejemplos de código (expanded)
        code_keywords = [
            'ejemplo', 'código', 'implementar', 'cómo hacer', 'muestra', 'muéstrame',
            'dame', 'déjame', 'quiero ver', 'necesito', 'ayúdame con', 'cómo crear',
            'programa', 'aplicación', 'proyecto', 'sample', 'demo', 'tutorial',
            'ver', 'mostrar', 'enseñar', 'enseñame', 'ejemplifica', 'ilustra',
            'código de', 'ejemplo de', 'muestra de', 'cómo se hace', 'cómo se crea',
            'cómo implementar', 'cómo usar', 'cómo trabajar con'
        ]
        
        # Palabras clave para explicaciones de conceptos (expanded)
        concept_keywords = [
            'qué es', 'explicar', 'concepto', 'definir', 'significa', 'para qué sirve',
            'cuál es', 'describe', 'características', 'ventajas', 'desventajas',
            'definición', 'explicación', 'qué significa', 'qué hace', 'cómo funciona',
            'en qué consiste', 'qué representa', 'qué implica'
        ]
        
        # Palabras clave para sintaxis (expanded)
        syntax_keywords = [
            'sintaxis', 'syntax', 'formato', 'escribir', 'declarar', 'cómo declarar',
            'estructura', 'palabra clave', 'keyword', 'operador', 'cómo se escribe',
            'cómo se declara', 'cómo se define', 'cómo se estructura', 'cómo se usa',
            'cómo se implementa', 'cómo se crea', 'cómo se define'
        ]
        
        # Verificar si es una pregunta sobre ejemplos de código
        if any(keyword in question_lower for keyword in code_keywords):
            return 'code_example'
        
        # Verificar si es una pregunta sobre conceptos
        if any(keyword in question_lower for keyword in concept_keywords):
            return 'concept_explanation'
        
        # Verificar si es una pregunta sobre sintaxis
        if any(keyword in question_lower for keyword in syntax_keywords):
            return 'syntax_help'
        
        # Verificar patrones específicos que indican solicitud de ejemplos
        if any(pattern in question_lower for pattern in [
            'cómo crear', 'cómo hacer', 'cómo implementar', 'cómo usar',
            'cómo trabajar', 'cómo desarrollar', 'cómo programar'
        ]):
            return 'code_example'
        
        # Verificar si la pregunta contiene palabras que sugieren ejemplos
        if any(word in question_lower for word in ['ejemplo', 'código', 'muestra', 'dame', 'muéstrame']):
            return 'code_example'
        
        # Por defecto, usar ayuda general
        return 'general_help'
    
    def retrieve_relevant_chunks(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Recuperar chunks relevantes usando embeddings - MEJORADO"""
        # Generar embedding de la consulta
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Búsqueda inicial con más resultados
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results * 3  # Obtener más resultados para re-ranking
        )
        
        # Re-ranking con cross-encoder
        if len(results['documents'][0]) > 0:
            pairs = [[query, doc] for doc in results['documents'][0]]
            scores = self.cross_encoder.predict(pairs)
            
            # Combinar documentos con scores
            doc_scores = list(zip(results['documents'][0], scores, results['metadatas'][0]))
            doc_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Retornar los mejores resultados con umbral más bajo
            top_results = []
            for doc, score, metadata in doc_scores[:n_results]:
                # Umbral más bajo para capturar más resultados útiles
                if score > 0.3:  # Reducido de 0.5 a 0.3
                    top_results.append({
                        'content': doc,
                        'score': score,
                        'metadata': metadata
                    })
            
            return top_results
        
        return []
    
    def clean_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Limpiar y preparar el contexto para el prompt - MEJORADO"""
        context_parts = []
        
        for chunk in chunks:
            # Limpiar el contenido del chunk
            content = chunk['content']
            
            # Remover caracteres extraños y normalizar
            content = re.sub(r'[^\w\s\.\,\;\:\!\?\(\)\[\]\{\}\+\-\*\/\=\<\>\"\'\n\r\t]', '', content)
            content = re.sub(r'\s+', ' ', content)
            content = content.strip()
            
            # Umbral más bajo para incluir más contenido
            if chunk['score'] > 0.3 and len(content) > 20:  # Reducido de 0.5 a 0.3
                context_parts.append(content)
        
        return "\n\n".join(context_parts)
    
    def generate_response(self, context: str, question: str, question_type: str) -> str:
        """Generar respuesta usando el modelo LLM o modo de recuperación - MEJORADO"""
        if self.model is None:
            # Modo de solo recuperación - proporcionar respuestas estructuradas
            if not context:
                # Respuesta más útil cuando no hay contexto
                if question_type == 'code_example':
                    return """Aquí tienes un ejemplo básico de código en C# y .NET:

**Ejemplo de programa básico en C#:**
```csharp
using System;

namespace MiPrimerPrograma
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("¡Hola Mundo desde C#!");
            
            // Variables y tipos de datos
            string nombre = "Desarrollador";
            int edad = 25;
            double salario = 50000.50;
            
            Console.WriteLine($"Nombre: {nombre}");
            Console.WriteLine($"Edad: {edad}");
            Console.WriteLine($"Salario: ${salario:F2}");
            
            // Estructuras de control
            if (edad >= 18)
            {
                Console.WriteLine("Eres mayor de edad");
            }
            
            // Bucle for
            for (int i = 1; i <= 5; i++)
            {
                Console.WriteLine($"Iteración {i}");
            }
        }
    }
}
```

**Ejemplo de clase en C#:**
```csharp
public class Persona
{
    public string Nombre { get; set; }
    public int Edad { get; set; }
    
    public Persona(string nombre, int edad)
    {
        Nombre = nombre;
        Edad = edad;
    }
    
    public void Presentarse()
    {
        Console.WriteLine($"Hola, soy {Nombre} y tengo {Edad} años");
    }
}
```

¿Te gustaría ver ejemplos más específicos de algún tema en particular?"""
                elif question_type == 'concept_explanation':
                    return """Aquí tienes información general sobre C# y .NET:

**C#** es un lenguaje de programación moderno, orientado a objetos y de propósito general desarrollado por Microsoft como parte de la plataforma .NET.

**Características principales de C#:**
- Tipado estático y seguro
- Orientado a objetos
- Garbage collection automático
- LINQ para consultas de datos
- Soporte para programación asíncrona
- Multiplataforma

**.NET** es una plataforma de desarrollo que incluye:
- Common Language Runtime (CLR)
- Framework Class Library (FCL)
- Herramientas de desarrollo
- Soporte para múltiples lenguajes

¿Te gustaría que profundice en algún aspecto específico?"""
                elif question_type == 'syntax_help':
                    return """Aquí tienes información sobre la sintaxis básica de C#:

**Declaración de variables:**
```csharp
int numero = 10;
string texto = "Hola";
bool activo = true;
double precio = 19.99;
```

**Declaración de métodos:**
```csharp
public void MetodoVacio() { }
public int MetodoConRetorno() { return 42; }
public string MetodoConParametros(string nombre) { return $"Hola {nombre}"; }
```

**Declaración de clases:**
```csharp
public class MiClase
{
    public string Propiedad { get; set; }
    
    public MiClase() { }
    
    public void MiMetodo() { }
}
```

¿Necesitas ayuda con alguna sintaxis específica?"""
                else:
                    return "No encontré información específica para tu pregunta. ¿Podrías reformularla o ser más específico?"
            
            # Crear respuesta estructurada basada en el contexto
            if question_type == 'code_example':
                # Para ejemplos de código - respuesta más específica
                return f"Aquí tienes información relevante con ejemplos de código:\n\n{context[:800]}..."
            elif question_type == 'concept_explanation':
                # Para explicaciones de conceptos
                return f"Basándome en la información disponible:\n\n{context[:600]}..."
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
        """Proceso completo de chat RAG - versión MEJORADA"""
        # 1. Clasificar pregunta
        question_type = self.classify_question(question)
        
        # 2. Recuperar contexto relevante
        relevant_chunks = self.retrieve_relevant_chunks(question, n_results=3)
        
        # 3. Preparar contexto limpio
        context = self.clean_context(relevant_chunks)
        
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