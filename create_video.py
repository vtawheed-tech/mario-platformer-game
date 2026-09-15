import os
import shutil
import cv2
import numpy as np
from manim import *
import math

def remove_background(input_path, output_path):
    img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        return

    if img.shape[2] == 3:
        # Convert to BGRA
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    h, w = img.shape[:2]
    mask = np.zeros((h+2, w+2), np.uint8)

    # Extract RGB only for floodFill
    img_rgb = img[:, :, :3].copy()

    # We flood fill from all 4 corners to isolate the bird from the background
    diff = (20, 20, 20)
    for pt in [(0, 0), (0, h-1), (w-1, 0), (w-1, h-1)]:
        cv2.floodFill(img_rgb, mask, pt, (0, 0, 0), diff, diff, cv2.FLOODFILL_MASK_ONLY)

    mask = mask[1:-1, 1:-1]
    mask = cv2.GaussianBlur(mask * 255, (5, 5), 0)

    img[:, :, 3] = 255 - mask
    cv2.imwrite(output_path, img)

class BirdFlight(Scene):
    def construct(self):
        self.camera.background_color = "#112233"

        original_image = "bird_original.png"
        processed_image = "images/bird.png"

        os.makedirs("images", exist_ok=True)

        fallback = "/tmp/file_attachments/file_000000004690820ba333fe39c24b0272.png"
        if not os.path.exists(original_image):
            if os.path.exists(fallback):
                shutil.copy(fallback, original_image)
            else:
                original_image = None

        if original_image and not os.path.exists(processed_image):
            remove_background(original_image, processed_image)

        if not os.path.exists(processed_image):
            bird = Text("Missing bird.png")
            self.add(bird)
            self.wait(15)
            return

        bird = ImageMobject(processed_image)
        bird.height = config.frame_height * 0.6

        def update_bird(mob, dt):
            if not hasattr(mob, 't'):
                mob.t = 0
            mob.t += dt

            y = math.sin(mob.t * 3) * 0.4

            new_angle = math.sin(mob.t * 2) * 0.05
            if not hasattr(mob, 'current_angle'):
                mob.current_angle = 0

            delta_angle = new_angle - mob.current_angle
            mob.rotate(delta_angle)
            mob.current_angle = new_angle

            x = -config.frame_width * 0.3 + mob.t * 0.4
            mob.move_to([x, y, 0])

        bird.add_updater(update_bird)

        self.add(bird)
        self.wait(15)

if __name__ == "__main__":
    import subprocess
    subprocess.run(["manim", "-qm", __file__, "BirdFlight"])
