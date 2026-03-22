from pipeline.align_timeline import process_video
from pathlib import Path
from pipeline.extract_frames import extract_keyframes, deduplicate_frames
from pipeline.ocr import ocr_all_frames, clean_all_results
from pipeline.transcribe_text import transcriber

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
    merged_transcript_path = process_video(cleaned_results, whisper_segments, Path(FILE_NAME).stem, OUTPUT_PATH)
    print("step 4 done: merged transcript saved")
    print(f"All done! Merged transcript available at: {merged_transcript_path}")


if __name__ == '__main__':
    main()
