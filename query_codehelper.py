from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
from transformers import pipeline

# Conectar con la base vectorial
client = PersistentClient(path="./vector_db")
collection = client.get_collection("codehelper_csharp")

# Cargar modelo de embeddings
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# Cargar traductor inglés → español
translator = pipeline("translation_en_to_es", model="Helsinki-NLP/opus-mt-en-es")

# Pregunta del usuario
query = input("Escribí tu pregunta sobre C# o .NET: ")

# Generar embedding y buscar
embedding = model.encode(query).tolist()
results = collection.query(query_embeddings=[embedding], n_results=3)

# Mostrar resultados con opción de ver original
print("\n🔍 Resultados más relevantes (traducidos al español):")
for i, doc in enumerate(results["documents"][0]):
    print(f"\n🔹 Fragmento {i+1}:")

    # Traducción al español
    translated = translator(doc[:500])[0]["translation_text"]
    print(translated)

    # Preguntar si quiere ver el original
    ver_original = input("¿Querés ver el texto original en inglés? (s/n): ").strip().lower()
    if ver_original == "s":
        print("\n Original:\n" + doc[:500])
