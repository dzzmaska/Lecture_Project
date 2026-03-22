from extract_frames import extract_keyframes, deduplicate_frames
from ocr import ocr_all_frames, clean_all_results
from transcribe_text import transcriber
from pathlib import Path

#Handling paths with pathlib;
FILE_NAME = "lecture_2.mp4" #fix this
BIG_FOLDER = Path(__file__).resolve().parent.parent
VIDEO_PATH = BIG_FOLDER / "media" / f"{Path(FILE_NAME).stem}.mp4"
FRAMES_PATH = BIG_FOLDER / "frames"
OUTPUT_PATH = BIG_FOLDER / "output"
TRANSCRIPTION = f"{OUTPUT_PATH}/{Path(FILE_NAME).stem}_transcription.txt"
TRANSCRIPTION_OCR = f"{OUTPUT_PATH}/{Path(FILE_NAME).stem}_ocr_transcription.txt"
#just a helper function to extract the frame index from the filename
def _sec_to_hms(seconds: float) -> str:
    import datetime
    return str(datetime.timedelta(seconds=int(seconds)))

def process_video(FULL_VIDEO_PATH: str, language: str = "en") -> str:

    # Step 1 — Extract & deduplicate frames
    extract_keyframes(str(FULL_VIDEO_PATH), str(FRAMES_PATH), fps=0.02)
    #this function automatically deletes frames that are too similar based on hashing, 
    deduplicate_frames(str(FRAMES_PATH), hash_threshold=5)
    print("step 1 done: frames extracted and deduplicated")
    # Step 2 — OCR on frames
    results = ocr_all_frames(str(FRAMES_PATH)) #Returns ocr soup for all frames without cleaning; we will clean it in the next step.
    #Here we clean the ocr soup by applying all the regex patterns
    cleaned_results = clean_all_results(results, fps=0.02)  # Assuming we do a frame in 50 seconds (0.02 fps) 
    print("step 2 done: OCR completed and results cleaned")

    # Step 3 — Transcribe audio
    whisper_segments = transcriber(str(FULL_VIDEO_PATH), language)
    print("step 3 in action: audio is being transcribed")
    
    #Here we write the transcribed text and the cleaned OCR text to separate files with timestamps. 
    #This is useful for debugging and also gives us a clear view of what the raw outputs look like before
    """
        with open(TRANSCRIPTION, "w", encoding="utf-8") as f:
        for segment in whisper_segments:
            start = _sec_to_hms(segment.start)
            end   = _sec_to_hms(segment.end)
            f.write(f"[{start} --> {end}] {segment.text.strip()}\n") # Add a newline after each segment for readability    
    print("step 3 done: audio transcribed")

    with open(TRANSCRIPTION_OCR, "w", encoding="utf-8") as f:
        for item in cleaned_results:
            f.write(f"--- {item['frame']} ---\n")
            f.write(f"Timestamp: {item['timestamp']}\n")
            f.write(f"Start: {item['start']}\n")
            f.write(f"End: {item['end']}\n")
            f.write(item['text'] + "\n\n")  # Add extra newline for readability
    print("step 4 done: OCR results written to file")

    """
    # Step 4 — Merge into one timeline
    timeline = []

    # Add OCR results
    for item in cleaned_results:
        timeline.append({
            "timestamp_sec": item["start"],  # numeric seconds for sorting
            "timestamp_hms": item["timestamp"],
            "type": "SLIDE",
            "text": item["text"]
        })

    # Add whisper segments
    for segment in whisper_segments:
        timeline.append({
            "timestamp_sec": segment.start,
            "timestamp_hms": _sec_to_hms(segment.start),
            "type": "SPEECH",
            "text": f"{segment.text.strip()}"
        })

    # Sort everything by timestamp
    timeline.sort(key=lambda x: x["timestamp_sec"])
    print("step 4 done: timeline merged and sorted")

    
    # Step 5 — Save merged transcript
    stem = Path(FULL_VIDEO_PATH).stem
    MERGED = OUTPUT_PATH / f"{stem}_merged_transcript.txt"

    with open(MERGED, "w", encoding="utf-8") as f:
        f.write("=== LECTURE TRANSCRIPT ===\n\n")
        for entry in timeline:
            f.write(f"[{entry['timestamp_hms']}] {entry['type']}: {entry['text']}\n\n")

    print("step 5 done: merged transcript saved")
    return str(MERGED)  # return path for summarizer to use

process_video(FULL_VIDEO_PATH=str(VIDEO_PATH), language="en")
