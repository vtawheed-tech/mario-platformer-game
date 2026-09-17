import os
import requests
import shutil
from moviepy.editor import *
import numpy as np

# Download Assets if not present
def download_file(url, filename):
    if not os.path.exists(filename):
        print(f"Downloading {filename}...")
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        r = requests.get(url, stream=True, headers=headers)
        with open(filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
        print(f"Saved {filename}")

# Note: For better quality we could use video assets if we had them, but for this task we use what we can get programatically
# We use a more fitting audio file from wikimedia for the savannah (traditional african drums/music or ambient if possible)
# Or we can use another audio. We'll download open source assets directly.
bg_url = "https://upload.wikimedia.org/wikipedia/commons/a/ac/African_Buffalo_Grazing_in_Kidepo_Valley_National_Park%2C_Uganda_02.jpg"
lion_url = "https://upload.wikimedia.org/wikipedia/commons/2/21/Lion4.png"
# African drums/savannah style royalty free from wikimedia
audio_url = "https://upload.wikimedia.org/wikipedia/commons/5/52/African_Drums.ogg"

os.makedirs("images", exist_ok=True)
download_file(bg_url, "images/savannah_background.jpg")
download_file(lion_url, "images/lion.png")
download_file(audio_url, "images/music.ogg")

# ----------------- Video Generation -----------------

# Resolution 16:9
RESOLUTION = (1920, 1080)
DURATION = 20

# Load images
print("Generating video...")
bg = ImageClip("images/savannah_background.jpg").resize(RESOLUTION)
lion = ImageClip("images/lion.png")

# Make the background a video clip
bg_clip = bg.set_duration(DURATION)

# Make lion smaller, keeping its aspect ratio
lion = lion.resize(height=400)

# Simulate walking by slightly bobbing up and down while moving right
def lion_pos(t):
    # x moves from left to right
    x = int(-lion.w + (1920 + lion.w) * (t / DURATION))
    # y bobs up and down slightly to simulate steps
    y = int(1080 - 550 + np.sin(t * 10) * 15)
    return (x, y)

lion_clip = lion.set_position(lion_pos).set_duration(DURATION)

video = CompositeVideoClip([bg_clip, lion_clip])

# Add audio
try:
    audio = AudioFileClip("images/music.ogg")
    # Loop audio if it's shorter than the video
    if audio.duration < DURATION:
        from moviepy.audio.fx.all import audio_loop
        audio = audio_loop(audio, duration=DURATION)
    else:
        audio = audio.subclip(0, DURATION)
    video = video.set_audio(audio)
except Exception as e:
    print(f"Warning: Could not add audio: {e}")

# Write out
video.write_videofile("lion_savannah.mp4", fps=24, codec='libx264', audio_codec='aac')
print("Video generated: lion_savannah.mp4")
