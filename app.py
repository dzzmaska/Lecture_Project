import shutil, json
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pipeline.align_timeline import process_video
from pipeline.extract_frames import extract_keyframes, deduplicate_frames
from pipeline.ocr import ocr_all_frames, clean_all_results
from pipeline.transcribe_text import transcriber
from pipeline.chunking import chunk_text
from pipeline.summarize import summarize_chunks, chroma_client
from chromadb.utils import embedding_functions
from pydantic import BaseModel
from fastapi import Body
import ollama
import ollama

# This accesses the SAME persistent collection that summarize_chunks() populated
ef = embedding_functions.DefaultEmbeddingFunction()
col = chroma_client.get_or_create_collection("lecture", embedding_function=ef)

BIG_FOLDER = Path(__file__).resolve().parent
MEDIA_PATH = BIG_FOLDER / "media"
FRAMES_PATH = BIG_FOLDER / "frames"
OUTPUT_PATH = BIG_FOLDER / "output"

for p in [MEDIA_PATH, FRAMES_PATH, OUTPUT_PATH]:
    p.mkdir(parents=True, exist_ok=True)



app = FastAPI()
class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []  # [{"role": "user"/"assistant", "content": "..."}]

@app.post("/chat")
async def chat(req: ChatRequest):
    # Retrieve relevant chunks from ChromaDB
    results = col.query(query_texts=[req.message], n_results=6)
    context = "\n\n".join(results["documents"][0])

    # Build messages: system prompt + history + new user message
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant answering questions about a university lecture. "
                "Keep answers SHORT and direct — 4 to 6 sentences maximum. "
                "No lengthy explanations unless the user explicitly asks for more detail. "
                "Use the lecture context below to answer accurately.\n\n"
                f"LECTURE CONTEXT:\n{context}"
            )
        },
        *req.history,
        {"role": "user", "content": req.message}
    ]

    response = ollama.chat(
    model="phi",
    messages=messages,
    options={"num_predict": 250})  # max tokens in the reply

    reply = response["message"]["content"]

    return {"reply": reply}

@app.post("/summarize")
async def summarize_video(file: UploadFile = File(...)):
    if not file.filename.endswith(".mp4"):
        raise HTTPException(status_code=400, detail="Only .mp4 files are supported.")

    stem = Path(file.filename).stem
    video_path = MEDIA_PATH / file.filename

    # Save uploaded file
    with open(video_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        extract_keyframes(str(video_path), str(FRAMES_PATH), fps=0.02)
        deduplicate_frames(str(FRAMES_PATH), hash_threshold=5)

        results = ocr_all_frames(str(FRAMES_PATH))
        cleaned_results = clean_all_results(results, fps=0.02)

        whisper_segments = transcriber(str(video_path), "en")

        merged = process_video(cleaned_results, whisper_segments, stem, OUTPUT_PATH)

        chunks, _ = chunk_text(merged)
        chunked_path = OUTPUT_PATH / f"{stem}_chunked_transcript.json"
        with open(chunked_path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)

        summaries = summarize_chunks(chunked_path)

        return {"status": "ok", "summary": summaries}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return FileResponse("static/index.html")