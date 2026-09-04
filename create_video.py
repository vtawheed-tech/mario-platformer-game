import edge_tts
import asyncio
import os
import glob
from moviepy import ImageClip, concatenate_videoclips, AudioFileClip
from PIL import Image

text = """Gurez Valley, a pristine gem nestled in the high Himalayas of Kashmir.
For centuries, it was part of the ancient Silk Route connecting the Kashmir Valley with Gilgit.
Surrounded by snow-capped mountains, it is home to the Dard Shin people, who speak the Shina language.
The majestic Kishanganga River flows through the valley, offering breathtaking views.
The pyramid-shaped Habba Khatoon peak stands tall, named after the famous Kashmiri poetess.
During winters, Gurez remains cut off from the rest of the world due to heavy snowfall.
But in summer, the valley transforms into a lush green paradise, dotted with traditional wooden houses.
Gurez is not just a destination; it is a journey into untouched beauty and serenity.
Experience the tranquility and untouched landscapes of the glorious Gurez Valley."""

async def generate_audio():
    communicate = edge_tts.Communicate(text, "en-US-GuyNeural")
    await communicate.save("narration.mp3")

def create_video():
    # 1. Generate Voice Narration
    asyncio.run(generate_audio())
    audio = AudioFileClip("narration.mp3")
    audio_duration = audio.duration
    print(f"Audio duration: {audio_duration}")

    # 2. Prepare Images
    image_files = sorted(glob.glob("images/img_*.jpg") + glob.glob("images/unsplash_*.jpg"))
    # Resize and crop images to fit 1920x1080 to avoid moviepy issues
    processed_images = []

    target_width, target_height = 1920, 1080
    for i, img_path in enumerate(image_files):
        try:
            with Image.open(img_path) as img:
                img_rgb = img.convert("RGB")
                # Calculate aspect ratio
                w, h = img_rgb.size
                aspect = w / h
                target_aspect = target_width / target_height

                if aspect > target_aspect:
                    # Image is wider than target, crop width
                    new_w = int(h * target_aspect)
                    offset = (w - new_w) / 2
                    img_rgb = img_rgb.crop((offset, 0, w - offset, h))
                else:
                    # Image is taller than target, crop height
                    new_h = int(w / target_aspect)
                    offset = (h - new_h) / 2
                    img_rgb = img_rgb.crop((0, offset, w, h - offset))

                img_rgb = img_rgb.resize((target_width, target_height), Image.Resampling.LANCZOS)
                proc_path = f"images/proc_{i}.jpg"
                img_rgb.save(proc_path)
                processed_images.append(proc_path)
        except Exception as e:
            print(f"Error processing {img_path}: {e}")

    # 3. Create Video Clips
    num_images = len(processed_images)
    if num_images == 0:
        print("No images found to create video.")
        return

    # To make it exactly 1 minute, loop or stretch? The audio dictates the length.
    # We can pad audio with silence if it's less than 60s, or just leave it at 40-50s
    # The requirement says "documentary should be of 1 minutes".
    # Let's see how long the audio is.
    target_duration = 60.0
    duration_per_image = target_duration / num_images

    clips = []
    for img_path in processed_images:
        clip = ImageClip(img_path).with_duration(duration_per_image)
        clips.append(clip)

    video = concatenate_videoclips(clips, method="compose")

    # If audio is shorter than 60 seconds, it will stop playing while images continue.
    video = video.with_audio(audio)

    # 4. Export Video
    video.write_videofile("Gurez_Documentary.mp4", fps=24, codec="libx264", audio_codec="aac")
    print("Video created successfully: Gurez_Documentary.mp4")

if __name__ == "__main__":
    create_video()
