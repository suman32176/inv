import time
import os
import tempfile
import zipfile
import platform
import subprocess
from moviepy.editor import (AudioFileClip, CompositeVideoClip, CompositeAudioClip, ImageClip,
                            TextClip, VideoFileClip)
from moviepy.audio.fx.audio_loop import audio_loop
from moviepy.audio.fx.audio_normalize import audio_normalize
import requests

def download_file(url, filename):
    print(f"Downloading file from {url} to {filename}...")
    with open(filename, 'wb') as f:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        f.write(response.content)
    print(f"File downloaded successfully: {filename}")

def search_program(program_name):
    try: 
        search_cmd = "where" if platform.system() == "Windows" else "which"
        print(f"Searching for {program_name} using command: {search_cmd}")
        return subprocess.check_output([search_cmd, program_name]).decode().strip()
    except subprocess.CalledProcessError:
        print(f"{program_name} not found.")
        return None

def get_program_path(program_name):
    program_path = search_program(program_name)
    if program_path:
        print(f"Found {program_name} at: {program_path}")
    else:
        print(f"{program_name} not found.")
    return program_path

def get_output_media(audio_file_path, timed_captions, background_video_data, video_server):
    OUTPUT_FILE_NAME = "rendered_video.mp4"
    magick_path = get_program_path("magick")
    if magick_path:
        os.environ['IMAGEMAGICK_BINARY'] = magick_path
        print(f"ImageMagick binary set to: {magick_path}")
    else:
        os.environ['IMAGEMAGICK_BINARY'] = '/usr/bin/convert'
        print("Using default ImageMagick path: /usr/bin/convert")
    
    visual_clips = []
    print("Downloading and processing background videos...")
    for (t1, t2), video_url in background_video_data:
        # Download the video file
        video_filename = tempfile.NamedTemporaryFile(delete=False).name
        download_file(video_url, video_filename)
        
        # Create VideoFileClip from the downloaded file
        print(f"Creating video clip from {video_filename}...")
        video_clip = VideoFileClip(video_filename)
        video_clip = video_clip.set_start(t1)
        video_clip = video_clip.set_end(t2)
        visual_clips.append(video_clip)
    
    audio_clips = []
    print("Loading audio file...")
    audio_file_clip = AudioFileClip(audio_file_path)
    audio_clips.append(audio_file_clip)
    print("Audio file loaded successfully.")

    print("Creating text clips for timed captions...")
    for (t1, t2), text in timed_captions:
        text_clip = TextClip(txt=text, fontsize=100, color="white", stroke_width=3, stroke_color="black", method="label")
        text_clip = text_clip.set_start(t1)
        text_clip = text_clip.set_end(t2)
        text_clip = text_clip.set_position(["center", 800])
        visual_clips.append(text_clip)
    
    print("Combining visual clips...")
    video = CompositeVideoClip(visual_clips)
    
    if audio_clips:
        print("Combining audio clips...")
        audio = CompositeAudioClip(audio_clips)
        video.duration = audio.duration
        video.audio = audio

    print(f"Rendering video to {OUTPUT_FILE_NAME}...")
    video.write_videofile(OUTPUT_FILE_NAME, codec='libx264', audio_codec='aac', fps=25, preset='veryfast')
    print("Video rendered successfully.")

    # Clean up downloaded files
    print("Cleaning up temporary video files...")
    for (t1, t2), video_url in background_video_data:
        video_filename = tempfile.NamedTemporaryFile(delete=False).name
        os.remove(video_filename)
        print(f"Removed temporary file: {video_filename}")

    return OUTPUT_FILE_NAME
