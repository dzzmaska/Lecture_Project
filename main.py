from pipeline.align_pipeline import process_video
import uvicorn
from pathlib import Path

video_path =  "media" // "lecture_2.mp4"

process_video(str(video_path), language="en")


if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)