import os
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient

# Crear cliente persistente con la nueva arquitectura de ChromaDB
client = PersistentClient(path="./vector_db")

# Crear o recuperar la colección
collection = client.get_or_create_collection("codehelper_csharp")

# Cargar modelo multilingüe para embeddings (soporta español e inglés)
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# Función para dividir texto en fragmentos (chunking básico)
def split_text(text, max_length=300):
    sentences = text.split(". ")
    chunks, current_chunk = [], ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_length:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

# Leer archivos de la carpeta /data (ignorando el índice)
data_dir = "./data"
doc_id = 0

for filename in os.listdir(data_dir):
    if filename.endswith(".txt") and "Index" not in filename:
        filepath = os.path.join(data_dir, filename)
        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()
            chunks = split_text(content)

            for chunk in chunks:
                embedding = model.encode(chunk).tolist()
                collection.add(
                    documents=[chunk],
                    embeddings=[embedding],
                    ids=[f"chunk_{doc_id}"]
                )
                doc_id += 1

# ¡Listo! Base guardada automáticamente en vector_db/
print(f"✅ Base vectorial creada con {doc_id} fragmentos.")
