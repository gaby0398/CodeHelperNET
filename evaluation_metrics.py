import numpy as np
from typing import List, Dict, Any
from sentence_transformers import CrossEncoder
from sklearn.metrics.pairwise import cosine_similarity
import time
import json

class RAGEvaluator:
    def __init__(self):
        """Inicializar evaluador de métricas RAG"""
        self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        
    def calculate_precision_at_k(self, relevant_docs: List[str], retrieved_docs: List[str], k: int = 5) -> float:
        """Calcular Precision@K"""
        if len(retrieved_docs) == 0:
            return 0.0
        
        relevant_retrieved = set(relevant_docs) & set(retrieved_docs[:k])
        return len(relevant_retrieved) / min(k, len(retrieved_docs))
    
    def calculate_recall_at_k(self, relevant_docs: List[str], retrieved_docs: List[str], k: int = 5) -> float:
        """Calcular Recall@K"""
        if len(relevant_docs) == 0:
            return 0.0
        
        relevant_retrieved = set(relevant_docs) & set(retrieved_docs[:k])
        return len(relevant_retrieved) / len(relevant_docs)
    
    def calculate_f1_score(self, precision: float, recall: float) -> float:
        """Calcular F1-Score"""
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)
    
    def calculate_ndcg_at_k(self, relevance_scores: List[float], k: int = 5) -> float:
        """Calcular NDCG@K (Normalized Discounted Cumulative Gain)"""
        if len(relevance_scores) == 0:
            return 0.0
        
        # DCG
        dcg = 0.0
        for i, score in enumerate(relevance_scores[:k]):
            dcg += score / np.log2(i + 2)  # i+2 porque log2(1) = 0
        
        # IDCG (ideal DCG)
        ideal_scores = sorted(relevance_scores, reverse=True)
        idcg = 0.0
        for i, score in enumerate(ideal_scores[:k]):
            idcg += score / np.log2(i + 2)
        
        return dcg / idcg if idcg > 0 else 0.0
    
    def calculate_response_time(self, query: str, retrieval_function, generation_function) -> float:
        """Medir tiempo de respuesta"""
        start_time = time.time()
        
        # Simular proceso RAG completo
        retrieved_docs = retrieval_function(query)
        response = generation_function(query, retrieved_docs)
        
        end_time = time.time()
        return end_time - start_time
    
    def evaluate_retrieval_quality(self, test_queries: List[Dict[str, Any]], retrieval_function) -> Dict[str, float]:
        """Evaluar calidad de recuperación"""
        precision_scores = []
        recall_scores = []
        f1_scores = []
        ndcg_scores = []
        
        for query_data in test_queries:
            query = query_data['query']
            relevant_docs = query_data['relevant_docs']
            
            # Obtener documentos recuperados
            retrieved_docs = retrieval_function(query)
            
            # Calcular métricas
            precision = self.calculate_precision_at_k(relevant_docs, retrieved_docs)
            recall = self.calculate_recall_at_k(relevant_docs, retrieved_docs)
            f1 = self.calculate_f1_score(precision, recall)
            
            precision_scores.append(precision)
            recall_scores.append(recall)
            f1_scores.append(f1)
            
            # Calcular NDCG (asumiendo scores de relevancia)
            relevance_scores = [1.0 if doc in relevant_docs else 0.0 for doc in retrieved_docs]
            ndcg = self.calculate_ndcg_at_k(relevance_scores)
            ndcg_scores.append(ndcg)
        
        return {
            'precision@5': np.mean(precision_scores),
            'recall@5': np.mean(recall_scores),
            'f1@5': np.mean(f1_scores),
            'ndcg@5': np.mean(ndcg_scores),
            'std_precision': np.std(precision_scores),
            'std_recall': np.std(recall_scores)
        }
    
    def evaluate_response_quality(self, test_queries: List[Dict[str, Any]], rag_function) -> Dict[str, Any]:
        """Evaluar calidad de respuestas generadas"""
        response_times = []
        response_lengths = []
        relevance_scores = []
        
        for query_data in test_queries:
            query = query_data['query']
            
            # Medir tiempo de respuesta
            start_time = time.time()
            response = rag_function(query)
            end_time = time.time()
            
            response_time = end_time - start_time
            response_times.append(response_time)
            
            # Medir longitud de respuesta
            response_lengths.append(len(response.split()))
            
            # Evaluar relevancia con cross-encoder
            relevance_score = self.cross_encoder.predict([[query, response]])
            relevance_scores.append(relevance_score)
        
        return {
            'avg_response_time': np.mean(response_times),
            'std_response_time': np.std(response_times),
            'avg_response_length': np.mean(response_lengths),
            'avg_relevance_score': np.mean(relevance_scores),
            'std_relevance_score': np.std(relevance_scores)
        }
    
    def create_test_dataset(self) -> List[Dict[str, Any]]:
        """Crear dataset de prueba para evaluación"""
        test_queries = [
            {
                'query': '¿Cómo declarar una variable en C#?',
                'relevant_docs': ['variable declaration', 'data types', 'syntax'],
                'expected_response_type': 'syntax_help'
            },
            {
                'query': 'Explica qué es un array en C#',
                'relevant_docs': ['arrays', 'collections', 'data structures'],
                'expected_response_type': 'concept_explanation'
            },
            {
                'query': 'Dame un ejemplo de un bucle for en C#',
                'relevant_docs': ['for loop', 'iteration', 'control structures'],
                'expected_response_type': 'code_example'
            },
            {
                'query': '¿Cómo usar Console.WriteLine?',
                'relevant_docs': ['console output', 'console.writeline', 'io operations'],
                'expected_response_type': 'code_example'
            },
            {
                'query': 'Explica qué es ADO.NET',
                'relevant_docs': ['ado.net', 'database access', 'data providers'],
                'expected_response_type': 'concept_explanation'
            }
        ]
        return test_queries
    
    def generate_evaluation_report(self, retrieval_metrics: Dict[str, float], 
                                 response_metrics: Dict[str, Any]) -> str:
        """Generar reporte de evaluación completo"""
        report = """
📊 REPORTE DE EVALUACIÓN DEL SISTEMA RAG
=========================================

🔍 MÉTRICAS DE RECUPERACIÓN:
- Precision@5: {:.3f} ± {:.3f}
- Recall@5: {:.3f} ± {:.3f}
- F1@5: {:.3f}
- NDCG@5: {:.3f}

⚡ MÉTRICAS DE RESPUESTA:
- Tiempo promedio de respuesta: {:.2f}s ± {:.2f}s
- Longitud promedio de respuesta: {:.1f} palabras
- Score de relevancia promedio: {:.3f} ± {:.3f}

📈 INTERPRETACIÓN:
- Precision@5: Indica qué tan precisos son los primeros 5 resultados
- Recall@5: Indica qué tan completa es la recuperación
- F1@5: Balance entre precisión y recall
- NDCG@5: Calidad del ranking considerando posición
- Tiempo de respuesta: Eficiencia del sistema
- Relevancia: Qué tan bien responde el modelo a las preguntas

🎯 RECOMENDACIONES:
""".format(
            retrieval_metrics['precision@5'], retrieval_metrics['std_precision'],
            retrieval_metrics['recall@5'], retrieval_metrics['std_recall'],
            retrieval_metrics['f1@5'],
            retrieval_metrics['ndcg@5'],
            response_metrics['avg_response_time'], response_metrics['std_response_time'],
            response_metrics['avg_response_length'],
            response_metrics['avg_relevance_score'], response_metrics['std_relevance_score']
        )
        
        # Agregar recomendaciones basadas en métricas
        if retrieval_metrics['precision@5'] < 0.7:
            report += "- Mejorar la calidad de embeddings o ajustar parámetros de búsqueda\n"
        if retrieval_metrics['recall@5'] < 0.6:
            report += "- Aumentar el número de resultados recuperados o mejorar chunking\n"
        if response_metrics['avg_response_time'] > 5.0:
            report += "- Optimizar el modelo de generación o usar caching\n"
        if response_metrics['avg_relevance_score'] < 0.6:
            report += "- Mejorar prompts o entrenar el modelo con más datos\n"
        
        return report

def run_evaluation(rag_system):
    """Ejecutar evaluación completa del sistema RAG"""
    evaluator = RAGEvaluator()
    test_queries = evaluator.create_test_dataset()
    
    print("🔬 Iniciando evaluación del sistema RAG...")
    
    # Evaluar recuperación
    retrieval_metrics = evaluator.evaluate_retrieval_quality(
        test_queries, 
        lambda q: rag_system.retrieve_relevant_chunks(q)
    )
    
    # Evaluar respuestas
    response_metrics = evaluator.evaluate_response_quality(
        test_queries,
        lambda q: rag_system.chat(q)
    )
    
    # Generar reporte
    report = evaluator.generate_evaluation_report(retrieval_metrics, response_metrics)
    print(report)
    
    # Guardar resultados
    results = {
        'retrieval_metrics': retrieval_metrics,
        'response_metrics': response_metrics,
        'test_queries': test_queries
    }
    
    with open('evaluation_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("✅ Resultados guardados en 'evaluation_results.json'")
    
    return results

if __name__ == "__main__":
    # Ejemplo de uso
    from rag_chatbot import RAGChatbot
    
    chatbot = RAGChatbot()
    results = run_evaluation(chatbot) 