import json
from pathlib import Path
#just a helper function to extract the frame index from the filename
def _sec_to_hms(seconds: float) -> str:
    import datetime
    return str(datetime.timedelta(seconds=int(seconds)))

def process_video(cleaned_results: list, whisper_segments: list, FILE_NAME_STEM: str, OUTPUT_PATH: Path):

    
   # Merge into one timeline
    timeline = []

    # Add OCR results
    for item in cleaned_results:
        timeline.append({
            "timestamp_hms_start": _sec_to_hms(item["start"]),  # human-readable timestamp
            "timestamp_hms_end": _sec_to_hms(item["end"]),  # human-readable timestamp
            "type": "SLIDE",
            "text": item["text"]
        })

    # Add whisper segments
    for segment in whisper_segments:
        timeline.append({
            "timestamp_hms_start": _sec_to_hms(segment.start),
            "timestamp_hms_end": _sec_to_hms(segment.end),
            "type": "SPEECH",
            "text": f"{segment.text.strip()}"
        })

    # Sort everything by timestamp
    timeline.sort(key=lambda x: x["timestamp_hms_start"])
    print("step 4 done: timeline merged and sorted")

    
    #Save merged transcript
    MERGED = OUTPUT_PATH / f"{FILE_NAME_STEM}_merged_transcript.json"

    with open(MERGED, "w", encoding="utf-8") as f:
        json.dump(timeline, f, indent=2, ensure_ascii=False)

    return str(MERGED)  # return path for summarizer to use
