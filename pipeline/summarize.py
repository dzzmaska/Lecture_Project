from transformers import pipeline
from pathlib import Path

def summarize_chunk(chunk_text):
    prompt = f"""
    You are summarizing a university lecture.

    Focus on:
    - key concepts
    - definitions
    - important explanations

    Ignore:
    - filler speech
    - OCR noise

    TEXT:
    {chunk_text}
    """

    response = llm(prompt)  # your API call
    return response

def summarize_chunks(chunks):
    results = []

    for chunk in chunks:
        summary = summarize_chunk(chunk["text"])
        
        results.append({
            "summary": summary,
            "start": chunk["start"],
            "end": chunk["end"]
        })

    return results

def combine_summaries(summaries):
    combined_text = "\n".join([s["summary"] for s in summaries])

    prompt = f"""
    Combine these into a structured lecture summary.

    - Use sections
    - Remove repetition
    - Keep clarity

    TEXT:
    {combined_text}
    """

    return llm(prompt)