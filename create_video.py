import asyncio
import os
import requests
from PIL import Image
import edge_tts
from moviepy import (
    AudioFileClip,
    ImageClip,
    concatenate_videoclips,
)

# Configuration
NARRATION_TEXT = """
Nelson Rolihlahla Mandela was a South African anti-apartheid activist and politician who served as the first president of South Africa from 1994 to 1999.
He was the country's first black head of state and the first elected in a fully representative democratic election.
His government focused on dismantling the legacy of apartheid by tackling institutionalized racism and fostering racial reconciliation.
Ideologically an African nationalist and socialist, he served as the president of the African National Congress party from 1991 to 1997.
Mandela spent 27 years in prison, split between Robben Island, Pollsmoor Prison, and Victor Verster Prison, due to his anti-apartheid activities.
After his release in 1990, he negotiated with State President F. W. de Klerk to end apartheid and establish multiracial elections in 1994, which he won.
He remains a global icon for peace, justice, and human rights.
"""
AUDIO_FILE = "narration.mp3"
VIDEO_FILE = "mandela_documentary.mp4"
IMAGES_DIR = "images"
TARGET_RESOLUTION = (1920, 1080) # 16:9 ratio

# Image URLs to download (public domain / fair use equivalents)
IMAGE_URLS = [
    "https://upload.wikimedia.org/wikipedia/commons/0/02/Nelson_Mandela_1994.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/1/14/Nelson_Mandela-2008_%28edit%29.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/e/e6/Nelson_Mandela%2C_2000_%285%29.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/1/1f/Frederik_de_Klerk%2C_Nelson_Mandela_-_World_Economic_Forum_Annual_Meeting_1992.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/9/9e/Nelson_Mandela%2C_President_of_South_Africa%2C_arrives_at_Andrews_Air_Force_Base%2C_Maryland_for_a_state_visit._He_is_greeted_by_a_welcoming_committee_and_a_salute_by_an_honor_guard.jpg"
]

async def generate_narration():
    """Generates the MP3 narration using edge-tts."""
    print("Generating narration...")
    communicate = edge_tts.Communicate(NARRATION_TEXT, "en-US-GuyNeural")
    await communicate.save(AUDIO_FILE)
    print(f"Narration saved to {AUDIO_FILE}")

def download_images():
    """Downloads images from the specified URLs."""
    print("Downloading images...")
    os.makedirs(IMAGES_DIR, exist_ok=True)
    image_paths = []

    # Use a custom user agent to avoid 403 Forbidden errors from Wikimedia
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for i, url in enumerate(IMAGE_URLS):
        try:
            response = requests.get(url, stream=True, headers=headers)
            response.raise_for_status()
            ext = url.split('.')[-1]
            if len(ext) > 4: # handle query params or odd extensions
                ext = "jpg"
            file_path = os.path.join(IMAGES_DIR, f"mandela_{i}.{ext}")
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            image_paths.append(file_path)
            print(f"Downloaded {file_path}")
        except Exception as e:
            print(f"Failed to download {url}: {e}")
    return image_paths

def process_image(image_path, target_size=TARGET_RESOLUTION):
    """
    Resizes and pads the image to fit the 16:9 target size
    without distorting the original aspect ratio.
    """
    img = Image.open(image_path).convert("RGB")
    target_ratio = target_size[0] / target_size[1]
    img_ratio = img.width / img.height

    if img_ratio > target_ratio:
        # Image is wider than 16:9, fit to width
        new_width = target_size[0]
        new_height = int(new_width / img_ratio)
    else:
        # Image is taller than 16:9, fit to height
        new_height = target_size[1]
        new_width = int(new_height * img_ratio)

    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Create a black background image of the target size
    background = Image.new("RGB", target_size, (0, 0, 0))

    # Paste the resized image into the center of the background
    offset_x = (target_size[0] - new_width) // 2
    offset_y = (target_size[1] - new_height) // 2
    background.paste(img, (offset_x, offset_y))

    processed_path = f"{os.path.splitext(image_path)[0]}_processed.jpg"
    background.save(processed_path, "JPEG")
    return processed_path

def create_video():
    """Compiles the video using the narration and processed images."""
    print("Generating video...")

    # 1. Download images
    raw_images = download_images()
    if not raw_images:
        print("No images downloaded. Exiting.")
        return

    # 2. Process images to 16:9
    processed_images = [process_image(p) for p in raw_images]

    # 3. Load audio to get duration
    audio_clip = AudioFileClip(AUDIO_FILE)
    audio_duration = audio_clip.duration
    print(f"Audio duration: {audio_duration:.2f} seconds")

    # 4. Calculate duration per image
    duration_per_image = audio_duration / len(processed_images)

    # 5. Create ImageClips
    image_clips = []
    for img_path in processed_images:
        clip = ImageClip(img_path).with_duration(duration_per_image)
        image_clips.append(clip)

    # 6. Concatenate video clips
    video_clip = concatenate_videoclips(image_clips, method="compose")

    # 7. Add audio
    video_clip = video_clip.with_audio(audio_clip)

    # 8. Write to file
    video_clip.write_videofile(
        VIDEO_FILE,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=4
    )
    print(f"Video successfully saved to {VIDEO_FILE}")

async def main():
    # Ensure images dir exists
    os.makedirs(IMAGES_DIR, exist_ok=True)

    # Generate audio
    await generate_narration()

    # Create video
    create_video()

if __name__ == "__main__":
    asyncio.run(main())
