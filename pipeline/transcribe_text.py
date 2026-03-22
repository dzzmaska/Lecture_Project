from faster_whisper import WhisperModel

#Load the model (choices: tiny, base, small, medium, large)
model = WhisperModel("tiny", compute_type="int8")  # fast CPU

def transcriber(FILE_NAME, LANGUAGE):

    # Transcribe the file
    segments, _ = model.transcribe(f"{FILE_NAME}", language=f"{LANGUAGE}")

    return segments  # Return the segments for further processing if needed




# Goal here is that we were writing the transcription to a file with timestamps, 
# but for the align pipeline we just want to return the segments as a list of dictionaries
#  with start, end, and text. This way we can merge it with the OCR data more easily.

"""
Example usage:
transcriber(str(video_path), "en")
"""

""""

# Define output path for transcription
TRANSCRIPTION = f"{output_path}/{Path(FILE_NAME).stem}_transcription.txt"

# write the text in the file with timestamps;
with open(TRANSCRIPTION, "w", encoding="utf-8") as f:
    for segment in segments:
        start = _sec_to_hms(segment.start)
        end   = _sec_to_hms(segment.end)
        f.write(f"[{start} --> {end}] {segment.text.strip()}\n") # Add a newline after each segment for readability    
"""


