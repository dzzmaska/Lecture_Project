                      ffmpeg splits into 
                                   ↓
       audio                                    frames
         ↓                              ↓
   Whisper                           pyttersect 
    (transcription)              (slide/board text)
         ↓                                 ↓
                   └─────── merge ────┘
                                  ↓
       RAG system (chunk + embed + store)
                                  ↓
            Chat interface (ask questions)
