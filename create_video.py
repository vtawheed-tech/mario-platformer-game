import os
import requests
import asyncio
import edge_tts
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips
from PIL import Image
import numpy as np

# Configuration
ASPECT_RATIO = (1920, 1080)
OUTPUT_VIDEO = "nelson_mandela_documentary.mp4"
IMAGES_DIR = "images"
AUDIO_FILE = "narration.mp3"
VOICE = "en-US-ChristopherNeural" # Male voice

# Script for 1-minute narration (~130-150 words)
SCRIPT_TEXT = """
Nelson Mandela was a global icon of peace, resilience, and the fight against injustice.
Born in 1918 in South Africa, he dedicated his life to dismantling apartheid, a brutal system of racial segregation.
For his activism, Mandela was imprisoned for 27 long years, much of it on Robben Island.
Yet, captivity did not break his spirit; it amplified his moral authority.
Upon his release in 1990, he did not seek revenge, but reconciliation.
He led the negotiations that ended apartheid and, in 1994, became South Africa's first Black president in a fully representative democratic election.
Mandela's legacy teaches us that forgiveness is more powerful than hatred, and that a single individual's unwavering commitment to justice can truly change the world.
"""

# Specific high-quality image URLs (Wikimedia Commons)
IMAGE_URLS = [
    "https://upload.wikimedia.org/wikipedia/commons/0/02/Nelson_Mandela_1994.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/c/cd/Nelson_Mandela_1937.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/9/91/Nelson_Mandela_1990_%28cropped%29.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/4/43/Robben_Island_Prison_Cell.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/d/d3/Nelson_Mandela_with_Bill_Clinton.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/a/ae/Nelson_Mandela_-_2008_%28cropped%29.jpg"
]

def setup_directory():
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)

def download_images():
    print("Downloading images...")
    headers = {'User-Agent': 'NelsonMandelaVideoBot/1.0 (contact@example.com) python-requests/2.34'}
    local_images = []

    for i, url in enumerate(IMAGE_URLS):
        ext = url.split('.')[-1]
        if '?' in ext:
            ext = ext.split('?')[0]
        ext = ext.lower()
        if ext not in ['jpg', 'jpeg', 'png']:
            ext = 'jpg'

        filepath = os.path.join(IMAGES_DIR, f"image_{i}.{ext}")
        local_images.append(filepath)

        if not os.path.exists(filepath):
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded {filepath}")
            except Exception as e:
                print(f"Failed to download {url}: {e}")

    return local_images

async def generate_audio():
    print("Generating audio narration...")
    communicate = edge_tts.Communicate(SCRIPT_TEXT, VOICE)
    await communicate.save(AUDIO_FILE)
    print(f"Saved audio to {AUDIO_FILE}")

def resize_image_for_video(image_path, target_size=(1920, 1080)):
    # Open image
    img = Image.open(image_path)

    # Calculate aspect ratios
    target_ratio = target_size[0] / target_size[1]
    img_ratio = img.width / img.height

    if img_ratio > target_ratio:
        # Image is wider, crop width
        new_width = int(img.height * target_ratio)
        offset = (img.width - new_width) // 2
        img = img.crop((offset, 0, offset + new_width, img.height))
    elif img_ratio < target_ratio:
        # Image is taller, crop height
        new_height = int(img.width / target_ratio)
        offset = (img.height - new_height) // 2
        img = img.crop((0, offset, img.width, offset + new_height))

    # Resize to target size
    img = img.resize(target_size, Image.Resampling.LANCZOS)

    # Save processed image to a temporary file for moviepy
    temp_path = f"{image_path}_processed.jpg"
    img.convert('RGB').save(temp_path)
    return temp_path

def create_video(local_images):
    print("Assembling video...")

    # Load audio
    audio = AudioFileClip(AUDIO_FILE)
    duration = audio.duration

    print(f"Audio duration: {duration} seconds")

    # Process images and calculate duration per image
    processed_images = [resize_image_for_video(img) for img in local_images if os.path.exists(img)]

    if not processed_images:
        print("No images found to create video.")
        return

    duration_per_image = duration / len(processed_images)

    clips = []
    for img_path in processed_images:
        clip = ImageClip(img_path).set_duration(duration_per_image)
        # Optional: Add a simple crossfade effect by overlapping (moviepy 1.0.3 supports this)
        clips.append(clip)

    # Concatenate clips
    video = concatenate_videoclips(clips, method="compose")
    video = video.set_audio(audio)

    print("Writing video file...")
    video.write_videofile(
        OUTPUT_VIDEO,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        threads=4
    )
    print("Video creation complete!")

async def main():
    setup_directory()
    local_images = download_images()
    await generate_audio()
    create_video(local_images)

if __name__ == "__main__":
    asyncio.run(main())
