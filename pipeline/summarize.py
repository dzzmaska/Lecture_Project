import json
import ollama
import chromadb
from chromadb.utils import embedding_functions

def summarize_chunks(json_path):
    # Step 1: load
    with open(json_path) as f:
        chunks = json.load(f)

    # Step 2: embed
    client = chromadb.Client()
    ef = embedding_functions.DefaultEmbeddingFunction()
    col = client.create_collection("lecture", embedding_function=ef)
    col.add(
        ids=[str(i) for i in range(len(chunks))],
        documents=[c["text"] for c in chunks],
        metadatas=[{"type": c["type"], "start": c["start"]} for c in chunks]
    )

    # Step 3 + 4: retrieve + summarize
    queries = [
    "main topics and key concepts",
    "definitions and explanations", 
    "examples and exercises"]
    for query in queries:
        results = col.query(query_texts=[query], n_results=15)
        context = "\n\n".join(results["documents"][0])

        response = ollama.chat(
            model="phi",
            messages=[{"role": "user", "content": f"You are summarizing a university lecture. Write a clear, structured summary with: Key concepts Important definitions Bullet points :\n\n{context}"}])
    print(response["message"]["content"])
    return response["message"]["content"]
