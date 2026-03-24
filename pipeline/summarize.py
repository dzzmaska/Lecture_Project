import json
import ollama
import chromadb
from chromadb.utils import embedding_functions

# Module-level persistent client — shared with app.py
chroma_client = chromadb.PersistentClient(path="./chroma_db")
ef = embedding_functions.DefaultEmbeddingFunction()

def summarize_chunks(json_path):
    # Step 1: load
    with open(json_path) as f:
        chunks = json.load(f)

    # Step 2: embed into persistent collection (reset if exists)
    col = chroma_client.get_or_create_collection("lecture", embedding_function=ef)
    col.add(
        ids=[str(i) for i in range(len(chunks))],
        documents=[c["text"] for c in chunks],
        metadatas=[{"type": c["type"], "start": c["start"]} for c in chunks]
    )

    # Step 3: retrieve
    query = "main topics and key concepts"
    results = col.query(query_texts=[query], n_results=5)
    context = "\n\n".join(results["documents"][0])

    # Step 4: summarize — specific and constrained prompt
    response = ollama.chat(
        model="phi",
        messages=[{
            "role": "user",
            "content": (
                "Read the lecture text below and write a summary with exactly these three sections:\n"
                "1. Main Topic — one sentence\n"
                "2. Key Concepts — up to 3 bullet points\n"
                "3. Key Definitions — up to 3 bullet points\n\n"
                "Only summarize what is written. Do not describe what you are doing.\n\n"
                "LECTURE TEXT:\n"
                f"{context}"
        )
        }],
        options={"num_predict": 300}  # hard cap on output length
    )
    print("step 6 done: summarization completed")
    print(response["message"]["content"])
    return response["message"]["content"]
