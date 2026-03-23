## Pipeline Overview

This project processes video files into a searchable knowledge base using a two-branch extraction pipeline.

### How it works

**1. Ingestion — ffmpeg**  
The pipeline starts by feeding a video file into `ffmpeg`, which splits it into two parallel streams: the audio track and a sequence of frames.

**2a. Audio branch — Whisper**  
The extracted audio is passed to [OpenAI Whisper](https://github.com/openai/whisper) for speech-to-text transcription. The output is timestamped transcript chunks covering everything spoken in the video.

**2b. Visual branch — pytesseract OCR**  
The extracted frames are scanned with [pytesseract](https://github.com/madmaze/pytesseract) to capture any on-screen text — slides, whiteboards, code snippets, or captions — that wouldn't appear in the audio track.

**3. Merge**  
Transcript chunks and OCR results are combined into a single unified text corpus, preserving context and timeline from both sources.

**4. RAG system**  
The merged corpus is chunked into overlapping segments, embedded into a vector store, and indexed for semantic retrieval.

**5. Chat interface**  UNDER WORK
Users can ask natural language questions about the video. The system retrieves the most relevant chunks and generates grounded answers based on what was said and shown.

<img width="1173" height="867" alt="image" src="https://github.com/user-attachments/assets/d7d5a5f5-086c-4347-a9f9-b00b3d0d4cae" />

### Important Notes: The project is not in it's final state for now

### Dependencies

| Tool | Role |
|---|---|
| `ffmpeg` | Audio extraction and frame splitting |
| `openai-whisper` | Speech-to-text transcription |
| `pytesseract` | OCR on extracted frames |
| `ollama phi` | Summarizes the chunks |
| `ChromeDB` | Embedding and retrieval |
