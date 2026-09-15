import numpy as np
from moviepy import VideoClip
from PIL import Image, ImageDraw
import math

WIDTH, HEIGHT = 640, 480
DURATION = 15
FPS = 24

def draw_jungle_background(draw):
    # Sky
    draw.rectangle([0, 0, WIDTH, HEIGHT//2], fill=(135, 206, 235))
    # Ground
    draw.rectangle([0, HEIGHT//2, WIDTH, HEIGHT], fill=(34, 139, 34))

    # Trees
    def draw_tree(x, y):
        # Trunk
        draw.rectangle([x-10, y, x+10, y+100], fill=(139, 69, 19))
        # Leaves
        draw.ellipse([x-40, y-60, x+40, y+20], fill=(0, 100, 0))
        draw.ellipse([x-20, y-80, x+20, y], fill=(0, 128, 0))

    draw_tree(100, HEIGHT//2 - 50)
    draw_tree(540, HEIGHT//2 - 20)
    draw_tree(300, HEIGHT//2 - 80)

def make_frame(t):
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    draw_jungle_background(draw)

    # Stickman properties
    head_radius = 20
    center_x = WIDTH // 2
    center_y = HEIGHT // 2 + 50

    # Bounce body based on time
    bounce = math.sin(t * 10) * 10
    head_y = center_y - 80 + bounce

    # Draw head
    draw.ellipse([center_x - head_radius, head_y - head_radius,
                  center_x + head_radius, head_y + head_radius],
                 outline='black', width=3, fill='yellow')

    # Draw body
    body_end_y = head_y + 80
    draw.line([center_x, head_y + head_radius, center_x, body_end_y], fill='black', width=3)

    # Arms
    # Left arm
    l_arm_angle = math.sin(t * 8) * math.pi / 4 + math.pi / 4
    l_arm_x = center_x - 40 * math.sin(l_arm_angle)
    l_arm_y = head_y + head_radius + 10 + 40 * math.cos(l_arm_angle)
    draw.line([center_x, head_y + head_radius + 10, l_arm_x, l_arm_y], fill='black', width=3)

    # Right arm
    r_arm_angle = math.sin(t * 8 + math.pi) * math.pi / 4 - math.pi / 4
    r_arm_x = center_x - 40 * math.sin(r_arm_angle)
    r_arm_y = head_y + head_radius + 10 + 40 * math.cos(r_arm_angle)
    draw.line([center_x, head_y + head_radius + 10, r_arm_x, r_arm_y], fill='black', width=3)

    # Legs
    # Left leg
    l_leg_angle = math.sin(t * 10) * math.pi / 4 + math.pi / 6
    l_leg_x = center_x - 50 * math.sin(l_leg_angle)
    l_leg_y = body_end_y + 50 * math.cos(l_leg_angle)
    draw.line([center_x, body_end_y, l_leg_x, l_leg_y], fill='black', width=3)

    # Right leg
    r_leg_angle = math.sin(t * 10 + math.pi) * math.pi / 4 - math.pi / 6
    r_leg_x = center_x - 50 * math.sin(r_leg_angle)
    r_leg_y = body_end_y + 50 * math.cos(r_leg_angle)
    draw.line([center_x, body_end_y, r_leg_x, r_leg_y], fill='black', width=3)

    return np.array(img)

def create_video():
    clip = VideoClip(make_frame, duration=DURATION)
    clip.write_videofile("stickman_dancing.mp4", fps=FPS, codec="libx264")

if __name__ == "__main__":
    create_video()
