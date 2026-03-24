import ffmpeg
import os
from PIL import Image
import imagehash
from pathlib import Path

def extract_keyframes(VIDEO_PATH: str, output_dir: str, fps: float = 0.02):
    #fps=0.02 means 1 frame every 50 seconds (THE BEST for lectures)
    os.makedirs(output_dir, exist_ok=True)

    (
        ffmpeg
        .input(VIDEO_PATH, skip_frame='nokey')  # Only extract keyframes for efficiency
        .filter('fps', fps=fps)           # Sample rate — tune for your needs
        .output(
            f"{output_dir}/frame_%06d.jpg",
            video_bitrate='0',
            **{'qscale:v': 2}             # JPEG quality (2=high, 31=low)
        )
        .run(overwrite_output=True, quiet=True) #set quiet to False if there's an error
    )

#Does not work well for lectures with lots of slides, but good for talking heads.
#we can adjust the fps and hash_threshold to find the right balance for lecture videos FPS = 0.02 hash = 5
def deduplicate_frames(frames_dir: str, hash_threshold: int = 5):
    """
    Compare every frame against the last KEPT frame (anchor),
    not against the previous frame. Prevents drift accumulation.
    """
    frame_paths = sorted(Path(frames_dir).glob("*.jpg"))
    
    kept = []
    anchor_hash = None  # Hash of the last significantly different frame

    for path in frame_paths:
        current_hash = imagehash.phash(Image.open(path))

        if anchor_hash is None or (current_hash - anchor_hash) > hash_threshold:
            kept.append(path)
            anchor_hash = current_hash  # Only update anchor on a real change
        else:
            path.unlink()  # Remove duplicate

    print(f"Kept {len(kept)} / {len(frame_paths)} frames")
    print("step 1 done: frames extracted and deduplicated")
    return kept



#0.01 works pefectly for long lectures, but if the processor is good we can adjust it 
# to 0.1 for more frames (1 every 10 seconds). 
#You can experiment with this value based on the content of your videos and 
# the performance of your system.

#Example usage:
"""
extract_keyframes(str(video_path), str(frames_path), fps=0.02)
print("Cleaning up duplicates...")
deduplicate_frames(str(frames_path), hash_threshold=5)  # Adjust threshold based on your content
print("Done extracting and deduplicating frames.")
"""

