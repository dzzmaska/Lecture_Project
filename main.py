import json
from pipeline.align_timeline import process_video
from pathlib import Path
from pipeline.extract_frames import extract_keyframes, deduplicate_frames
from pipeline.ocr import ocr_all_frames, clean_all_results
from pipeline.transcribe_text import transcriber
from pipeline.chunking import chunk_text
from pipeline.summarize import summarize_chunks

FILE_NAME = "lecture_2.mp4" #We get this from user

#Handling paths with pathlib;
BIG_FOLDER = Path(__file__).resolve().parent
VIDEO_PATH = f"{BIG_FOLDER / 'media' / f'{Path(FILE_NAME).stem}.mp4'}"
FRAMES_PATH = f"{BIG_FOLDER / 'frames'}"
OUTPUT_PATH = BIG_FOLDER / 'output'
OUTPUT_PATH.mkdir(parents=True, exist_ok=True) # Creates the 'output' folder if it's missing
TRANSCRIPTION = f"{OUTPUT_PATH}/{Path(FILE_NAME).stem}_transcription.txt" #optional 
TRANSCRIPTION_OCR = f"{OUTPUT_PATH}/{Path(FILE_NAME).stem}_ocr_transcription.txt" #optional

def main():
    """
    # Step 1 — Extract & deduplicate frames
    extract_keyframes(str(VIDEO_PATH), str(FRAMES_PATH), fps=0.02)
    #this function automatically deletes frames that are too similar based on hashing, 
    deduplicate_frames(str(FRAMES_PATH), hash_threshold=5)
    print("step 1 done: frames extracted and deduplicated")

    # Step 2 — OCR on frames
    results = ocr_all_frames(str(FRAMES_PATH)) #Returns ocr soup for all frames without cleaning; we will clean it in the next step.
    #Here we clean the ocr soup by applying all the regex patterns
    cleaned_results = clean_all_results(results, fps=0.02)  # Assuming we do a frame in 50 seconds (0.02 fps) 
    print("step 2 done: OCR completed and results cleaned")

    # Step 3 — Transcribe audio
    whisper_segments = transcriber(str(VIDEO_PATH), "en")  # Returns list of segments with start, end, and text
    print("step 3 in action: audio is being transcribed")

    # Step 4 — align timeline of text and OCR and save
    merged_timeline_transcript = process_video(cleaned_results, whisper_segments, Path(FILE_NAME).stem, OUTPUT_PATH)
    print("step 4 done: merged transcript saved")
    
    # Step 5 — chunking
    #We can adjust the max_words and overlap_words to find the right balance for chunk size and context retention.
    chunks, av = chunk_text(merged_timeline_transcript)
    print(f"Average words per chunk: {av:.2f} (Best is between 500-1000 chars)")

    CHUNKED = OUTPUT_PATH / f"{Path(FILE_NAME).stem}_chunked_transcript.json"
    with open(CHUNKED, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    print(f"step 5 done: text has been chunked and file was saved at {CHUNKED}")
    """
    CHUNKED = OUTPUT_PATH / f"{Path(FILE_NAME).stem}_chunked_transcript.json"

    # Step 6 — summarization
    # We can summarize each chunk individually and then combine those summaries into a final structured summary of the lecture.
    summaries = summarize_chunks(CHUNKED)
    print("step 6 done: summarization completed")

if __name__ == '__main__':
    main()
