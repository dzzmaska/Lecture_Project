def split_large_entry(entry: dict, max_words: int) -> list[dict]:
    words = entry["text"].split()
    if len(words) <= max_words:
        return [entry]
    
    pieces = []
    for i in range(0, len(words), max_words):
        chunk_words = words[i:i + max_words]
        pieces.append({
            "start": entry["start"],
            "end": entry["end"],
            "type": entry["type"],
            "text": " ".join(chunk_words)
        })
    return pieces


def chunk_text(timeline, max_words=250, overlap_words=50):
    chunks = []
    current_chunk = []
    current_words = 0
    expanded = []

    for entry in timeline:
        expanded.extend(split_large_entry(entry, max_words))

    for entry in expanded:
        text = entry["text"].strip().replace("\n", " ")
        word_count = len(text.split())

        # flush buffer and save immediately
        if entry["type"] == "SLIDE":
            if current_chunk:
                chunks.append({
                    "start": current_chunk[0]["start"],
                    "end": current_chunk[-1]["end"],
                    "type": current_chunk[0]["type"],
                    "text": " ".join(c["text"] for c in current_chunk),
                })
                current_chunk = []
                current_words = 0
            chunks.append({
                "start": entry["start"],
                "end": entry["end"],
                "type": "SLIDE",
                "text": text,
            })
            continue

        # SPEECH: accumulate with overlap
        current_chunk.append({
            "start": entry["start"],
            "end": entry["end"],
            "type": entry["type"],
            "text": text,
        })
        current_words += word_count

        if current_words >= max_words:
            chunks.append({
                "start": current_chunk[0]["start"],
                "end": current_chunk[-1]["end"],
                "type": current_chunk[0]["type"],
                "text": " ".join(c["text"] for c in current_chunk),
            })
            overlap = []
            overlap_count = 0
            for c in reversed(current_chunk):
                overlap.insert(0, c)
                overlap_count += len(c["text"].split())
                if overlap_count >= overlap_words:
                    break
            current_chunk = overlap
            current_words = overlap_count

    #save remaining SPEECH chunks
    if current_chunk:
        chunks.append({
            "start": current_chunk[0]["start"],
            "end": current_chunk[-1]["end"],
            "type": current_chunk[0]["type"],
            "text": " ".join(c["text"] for c in current_chunk),
        })
    #this is very useful to understand the average chunk size and adjust the max_words and overlap_words accordingly.
    avg_chunk_char_count = sum(len(c["text"]) for c in chunks) / len(chunks)

    return chunks, avg_chunk_char_count
