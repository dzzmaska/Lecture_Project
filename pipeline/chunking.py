def chunk_text(timeline, max_words=500, overlap_words=100):
    chunks = []

    current_chunk = []
    current_words = 0

    i = 0
    while i < len(timeline):
        entry = timeline[i]
        text = entry["text"]
        word_count = len(text.split())

        # Format text based on type
        if entry["type"] == "slide":
            formatted_text = f"\n[SLIDE]\n{text}\n"
        else:
            formatted_text = f"{text}"

        current_chunk.append({
            "text": formatted_text,
            "start": entry["start"],
            "end": entry["end"]
        })

        current_words += word_count

        if current_words >= max_words:
            chunk_text = " ".join([c["text"] for c in current_chunk])

            chunks.append({
                "text": chunk_text,
                "start": current_chunk[0]["start"],
                "end": current_chunk[-1]["end"]
            })

            # Overlap logic
            overlap = []
            overlap_words_count = 0

            for c in reversed(current_chunk):
                overlap.insert(0, c)
                overlap_words_count += len(c["text"].split())
                if overlap_words_count >= overlap_words:
                    break

            current_chunk = overlap
            current_words = overlap_words_count

        i += 1

    # last chunk
    if current_chunk:
        chunk_text = " ".join([c["text"] for c in current_chunk])
        chunks.append({
            "text": chunk_text,
            "start": current_chunk[0]["start"],
            "end": current_chunk[-1]["end"]
        })
    chunks = chunk_text(timeline)

    for c in chunks[:2]:
        print("TIME:", c["start"], "-", c["end"])
        print(c["text"][:500])
        print("="*50)

    return chunks

"""
from pathlib import Path
chunk_text(Path("output/lecture_2_merged_transcript.json"))
"""