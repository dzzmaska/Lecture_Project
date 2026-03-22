from transformers import pipeline
from pathlib import Path

# This will download a default model (usually DistilBART) the first time you run it
summarizer = pipeline("summarization")

def open_my_file(name):
    try:
        #we don't need to close the file with WITH
        with open(f'{name}', "r", encoding="utf-8") as raw_text:
            text = raw_text.read()
    except OSError as problem:
        print(f"Ouch we have a problem back in summarizer: {problem}")
        text = None
    return text

def summarize_text(FILE_NAME):
    # 2. Read your generated text file
    lecture_text = open_my_file(FILE_NAME)
    SUMMARY = f"{Path(FILE_NAME).stem}_summary.txt"  # → "lecture_1_summary.txt"    
    # 3. Generate the summary (Note: we use a short snippet for the test)
    # You might want to test this with just a few paragraphs first!    

    summary = summarizer(
        lecture_text[:2000],          # Still testing on just the first 2000 characters!
        max_length=150,               # Give it a bit more room to write
        min_length=50,                # Ensure it doesn't just write one sentence
        do_sample=False,              # Keep it strictly factual
        num_beams=4,                  # Boost the sentence quality
        truncation=True               # Prevent it from crashing if the text is slightly too long
    )

    summary_text = summary[0]['summary_text']

    with open(SUMMARY, "w", encoding="utf-8") as f:
        f.write(summary_text)

    return summary_text  # ← return the text, not the filename
