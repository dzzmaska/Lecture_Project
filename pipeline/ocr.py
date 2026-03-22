import pytesseract
from PIL import Image
from pathlib import Path
import re

# Point to tesseract binary (Windows only)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 1. Compile regex patterns once for a major speed boost.
# 2. Removed case-duplicates.
# 3. Changed \n to (?:\n|$) to catch noise at the very end of the file.
COMPILED_PATTERNS = [
    re.compile(pattern, flags=re.IGNORECASE) for pattern in [
        r'Autosave.*?(?:\n|$)',
        r'File Home Insert.*?(?:\n|$)',
        r'Clipboard.*?(?:\n|$)',
        r'Click to add notes.*?(?:\n|$)',
        r'Slide \d+ of \d+.*?(?:\n|$)',
        r'Accessibility.*?(?:\n|$)',
        r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',  # timestamps
        r'Present in Teams.*?(?:\n|$)',
        r'Adobe Acrobat.*?(?:\n|$)',
        r'Replace Fonts.*?(?:\n|$)',
        r'English \(United.*?(?:\n|$)',
        r'^Search\s*$',  # only delete lines that are JUST the word "Search",
        r'Saved to this PC.*?(?:\n|$)',
    ]
]
# These patterns are designed to catch common UI elements and noise that appear in lecture slides when OCR is applied.
def is_noise(text: str, threshold: float = 0.3) -> bool:
    """Returns True if less than 30% of characters are normal ASCII letters/digits."""
    if not text:
        return True
    normal = sum(1 for c in text if c.isalnum() or c.isspace())
    return (normal / len(text)) < threshold

#this is useful for timestamping;
def get_frame_index(frame_name: str) -> int:
    return int(frame_name.split('_')[1].split('.')[0])

#usual command to extract text from an image using pytesseract; we use --psm 6 for block of text and --oem 3 for best accuracy
def extract_text(image_path: str) -> str:
    img = Image.open(image_path).convert('L')  # grayscale = faster
    text = pytesseract.image_to_string(img, config='--psm 6 --oem 3')
    return text.strip()

#in here we just call extract text function for each frame and store the results in a list of dictionaries; 
# we also sort the frames to ensure they are processed in the correct order
def ocr_all_frames(frames_dir: str) -> list[dict]:
    frame_paths = sorted(Path(frames_dir).glob("*.jpg"))
    results = []
    for path in frame_paths:
        text = extract_text(str(path))
        if text:
            results.append({"frame": path.name, "text": text})
    return results

#Here we clean the OCR soup by applying all the regex patterns and some additional cleaning steps to make the text more usable for summarization.
# We also filter out frames that become empty after cleaning, which are likely just noise.
def clean_text(text: str) -> str:
    # Use the pre-compiled patterns
    for pattern in COMPILED_PATTERNS:
        text = pattern.sub('', text)

    # Remove non-printable characters
    text = re.sub(r'[^\x20-\x7E\n]', '', text)
    
    # Fix broken hyphenated words (e.g. "algo-\nrithm" → "algorithm")
    text = re.sub(r'-\n', '', text)
    
    # Collapse multiple spaces
    text = re.sub(r' +', ' ', text)
    
    # Collapse more than 2 newlines into 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove lines that are just 1-2 characters (OCR noise)
    lines = text.split('\n')
    # Warning: This will delete lines that are genuinely just "IT" or "To". 
    # If you lose valid data, change > 2 to > 1.
    lines = [l for l in lines if len(l.strip()) > 2] 
    
    return '\n'.join(lines).strip()

#Here we just clean all the results using clean_text function; 
def clean_all_results(ocr_results: list[dict], fps: float) -> list[dict]:
    cleaned = []

    for result in ocr_results:

        text = clean_text(result['text'])
        if is_noise(result['text']):
            continue
        if text:  # skip frames that become empty after cleaning
            frame_index = get_frame_index(result['frame']) # extract frame index for timestamping
            timestamp = frame_index / fps  # convert frame index to seconds
            interval = 1 / fps  # duration of each frame in seconds
            cleaned.append({
                'frame': result['frame'],
                'timestamp': timestamp - interval,  # start time of the frame
                'start': timestamp - interval,
                'end': timestamp,
                'text': text
            })
    return cleaned

#calling functions to run the whole OCR and cleaning; 
#Example usage:
"""
results = ocr_all_frames(str(frames_path))
cleaned_results = clean_all_results(results, fps=0.02)  # Assuming we do a frame in 50 seconds
with open(TRANSCRIPTION_OCR, "w", encoding="utf-8") as f:
    for item in cleaned_results:
        f.write(f"--- {item['frame']} ---\n")
        f.write(f"Timestamp: {item['timestamp']}\n")
        f.write(f"Start: {item['start']}\n")
        f.write(f"End: {item['end']}\n")
        f.write(item['text'] + "\n\n")  # Add extra newline for readability
"""