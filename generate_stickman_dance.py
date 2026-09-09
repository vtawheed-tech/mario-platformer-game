import math
import cv2
import numpy as np
import imageio.v2 as imageio

# Configuration
WIDTH = 1280
HEIGHT = 720
FPS = 30
DURATION = 8  # seconds
TOTAL_FRAMES = FPS * DURATION
OUTPUT_FILE = "stickman_dance.mp4"

def create_background(frame_num):
    # Dark gradient background
    img = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

    # Stage floor (y = 520 to 720)
    floor_y = 520

    # Background gradient from top dark blue to slightly brighter navy near floor
    for y in range(HEIGHT):
        r = int(15 + (y / HEIGHT) * 20)
        g = int(15 + (y / HEIGHT) * 25)
        b = int(35 + (y / HEIGHT) * 45)
        img[y, :] = (b, g, r) # BGR

    # Floor area with grid pattern
    t = frame_num / FPS
    grid_offset = int((t * 100) % 40)

    # Draw floor line
    cv2.line(img, (0, floor_y), (WIDTH, floor_y), (100, 100, 180), 3, cv2.LINE_AA)

    # Floor perspective lines / grid
    cv2.rectangle(img, (0, floor_y), (WIDTH, HEIGHT), (20, 20, 40), -1)
    cv2.line(img, (0, floor_y), (WIDTH, floor_y), (120, 120, 200), 2, cv2.LINE_AA)

    # Floor horizontal lines
    for hy in range(floor_y, HEIGHT, 25):
        alpha = 0.3 + 0.7 * ((hy - floor_y) / (HEIGHT - floor_y))
        color = (int(100 * alpha), int(100 * alpha), int(180 * alpha))
        cv2.line(img, (0, hy), (WIDTH, hy), color, 1, cv2.LINE_AA)

    # Stage Spotlights / Disco Lights
    colors = [
        (255, 100, 100), # Cyan-ish in BGR (255,100,100 -> B=255, G=100, R=100)
        (100, 255, 100), # Greenish
        (100, 100, 255), # Reddish
        (255, 100, 255), # Magenta
        (100, 255, 255)  # Yellow
    ]

    c1 = colors[int(t * 2) % len(colors)]
    c2 = colors[int(t * 2 + 2) % len(colors)]

    # Spotlight 1 (Left top pointing to center)
    spot1_x = int(640 + math.sin(t * 3) * 250)
    pts1 = np.array([[100, 0], [300, 0], [spot1_x + 80, floor_y], [spot1_x - 80, floor_y]], np.int32)
    overlay = img.copy()
    cv2.fillPoly(overlay, [pts1], c1)
    cv2.addWeighted(overlay, 0.15, img, 0.85, 0, img)

    # Spotlight 2 (Right top pointing to center)
    spot2_x = int(640 + math.cos(t * 2.5) * 250)
    pts2 = np.array([[WIDTH - 300, 0], [WIDTH - 100, 0], [spot2_x + 80, floor_y], [spot2_x - 80, floor_y]], np.int32)
    overlay = img.copy()
    cv2.fillPoly(overlay, [pts2], c2)
    cv2.addWeighted(overlay, 0.15, img, 0.85, 0, img)

    # Stage lights circles on floor
    cv2.ellipse(img, (spot1_x, floor_y + 30), (120, 30), 0, 0, 360, c1, -1, cv2.LINE_AA)
    cv2.ellipse(img, (spot2_x, floor_y + 30), (120, 30), 0, 0, 360, c2, -1, cv2.LINE_AA)

    return img

def get_stickman_pose(frame_num):
    t = frame_num / FPS

    # Base position
    floor_y = 500

    # Determine dance phase (4 phases, 2s each)
    phase = int(t / 2) % 4
    phase_t = (t % 2) / 2.0  # 0 to 1 within phase

    center_x = 640
    center_y = floor_y - 180

    # Key joints initial positions relative to hip
    # Default stick man height approx 220px
    # Head, Neck, Torso, Hips, Left Arm (Shoulder, Elbow, Hand), Right Arm, Left Leg (Hip, Knee, Foot), Right Leg

    if phase == 0:
        # Phase 1: Hip Hop Bounce & Hand Wave
        bounce = abs(math.sin(t * math.pi * 3)) * 25
        center_y = floor_y - 180 + bounce
        center_x = 640 + math.sin(t * math.pi * 1.5) * 60

        body_angle = math.sin(t * math.pi * 3) * 0.1

        # Left arm waving high
        l_arm_angle = math.sin(t * math.pi * 6) * 0.5 - 2.2
        r_arm_angle = math.cos(t * math.pi * 6) * 0.5 + 0.8

        # Legs bending with bounce
        l_knee_bend = bounce * 0.8
        r_knee_bend = bounce * 0.8

        l_foot_x = center_x - 45
        r_foot_x = center_x + 45
        l_foot_y = floor_y
        r_foot_y = floor_y

    elif phase == 1:
        # Phase 2: Disco Pointer / Stayin' Alive
        bounce = abs(math.sin(t * math.pi * 4)) * 15
        center_y = floor_y - 185 + bounce

        # Side sway
        sway = math.sin(t * math.pi * 2) * 50
        center_x = 640 + sway

        # Disco arm point: right hand up-right, then down-left alternating
        beat_cycle = math.sin(t * math.pi * 3)
        if beat_cycle > 0:
            r_arm_angle = -2.3  # Pointing up right
            l_arm_angle = 1.2   # Down left
        else:
            r_arm_angle = 1.2   # Down right
            l_arm_angle = -2.3  # Pointing up left

        l_foot_x = center_x - 50
        r_foot_x = center_x + 50
        l_foot_y = floor_y
        r_foot_y = floor_y

    elif phase == 2:
        # Phase 3: High Knee Side Shuffle & Jump Spin
        # Check if doing a jump spin around 5.0 - 5.8s
        if 4.8 <= t <= 5.6:
            spin_progress = (t - 4.8) / 0.8
            jump_height = math.sin(spin_progress * math.pi) * 100
            center_y = floor_y - 180 - jump_height
            center_x = 640 + math.sin(spin_progress * math.pi * 2) * 80

            # Rotation effect
            rot = spin_progress * math.pi * 2
            r_arm_angle = -3.0 + rot
            l_arm_angle = 0.5 + rot
            l_foot_x = center_x - 25
            r_foot_x = center_x + 25
            l_foot_y = center_y + 110
            r_foot_y = center_y + 110
        else:
            center_x = 640 + math.sin(t * math.pi * 2) * 120
            center_y = floor_y - 180 + abs(math.sin(t * math.pi * 4)) * 20
            r_arm_angle = math.sin(t * math.pi * 4) * 1.2
            l_arm_angle = -math.sin(t * math.pi * 4) * 1.2

            l_foot_x = center_x - 40
            r_foot_x = center_x + 40
            l_foot_y = floor_y - max(0, math.sin(t * math.pi * 4)) * 40
            r_foot_y = floor_y - max(0, -math.sin(t * math.pi * 4)) * 40

    else:
        # Phase 4: Fast Floss / Freestyle & Victory Grand Pose
        if t < 7.2:
            # Floss motion
            floss_t = t * math.pi * 6
            center_x = 640 + math.sin(floss_t * 0.5) * 30
            center_y = floor_y - 180 + abs(math.sin(floss_t)) * 10

            arm_swing = math.sin(floss_t) * 1.5
            l_arm_angle = 0.8 + arm_swing
            r_arm_angle = 0.8 + arm_swing

            l_foot_x = center_x - 55
            r_foot_x = center_x + 55
            l_foot_y = floor_y
            r_foot_y = floor_y
        else:
            # Final Victory Pose!
            center_x = 640
            center_y = floor_y - 190
            l_arm_angle = -2.4 # Arms up in V shape
            r_arm_angle = 2.4
            l_foot_x = center_x - 60
            r_foot_x = center_x + 60
            l_foot_y = floor_y
            r_foot_y = floor_y

    # Calculate skeleton coordinates
    head_r = 28
    neck_len = 15
    torso_len = 70
    limb_len1 = 45 # Upper arm/leg
    limb_len2 = 45 # Lower arm/leg

    hip_x = center_x
    hip_y = center_y + 30

    neck_x = center_x
    neck_y = center_y - torso_len + 30

    head_x = center_x
    head_y = neck_y - head_r

    # Arms
    # Left Arm
    l_shoulder_x = neck_x - 10
    l_shoulder_y = neck_y + 10
    if phase == 2 and 4.8 <= t <= 5.6:
        l_elbow_x = l_shoulder_x + math.cos(l_arm_angle) * limb_len1
        l_elbow_y = l_shoulder_y + math.sin(l_arm_angle) * limb_len1
        l_hand_x = l_elbow_x + math.cos(l_arm_angle + 0.5) * limb_len2
        l_hand_y = l_elbow_y + math.sin(l_arm_angle + 0.5) * limb_len2
    else:
        l_elbow_x = l_shoulder_x + math.sin(l_arm_angle) * limb_len1
        l_elbow_y = l_shoulder_y + math.cos(l_arm_angle) * limb_len1
        l_hand_x = l_elbow_x + math.sin(l_arm_angle - 0.4) * limb_len2
        l_hand_y = l_elbow_y + math.cos(l_arm_angle - 0.4) * limb_len2

    # Right Arm
    r_shoulder_x = neck_x + 10
    r_shoulder_y = neck_y + 10
    if phase == 2 and 4.8 <= t <= 5.6:
        r_elbow_x = r_shoulder_x + math.cos(r_arm_angle) * limb_len1
        r_elbow_y = r_shoulder_y + math.sin(r_arm_angle) * limb_len1
        r_hand_x = r_elbow_x + math.cos(r_arm_angle - 0.5) * limb_len2
        r_hand_y = r_elbow_y + math.sin(r_arm_angle - 0.5) * limb_len2
    else:
        r_elbow_x = r_shoulder_x + math.sin(r_arm_angle) * limb_len1
        r_elbow_y = r_shoulder_y + math.cos(r_arm_angle) * limb_len1
        r_hand_x = r_elbow_x + math.sin(r_arm_angle + 0.4) * limb_len2
        r_hand_y = r_elbow_y + math.cos(r_arm_angle + 0.4) * limb_len2

    # Legs & Knees
    # Inverse kinematics / bending to reach feet
    def calc_knee(hx, hy, fx, fy, flip=False):
        dx = fx - hx
        dy = fy - hy
        dist = math.hypot(dx, dy)
        dist = min(dist, limb_len1 + limb_len2 - 2)
        mid_x = (hx + fx) / 2
        mid_y = (hy + fy) / 2

        # Distance from mid to knee
        h = math.sqrt(max(0, limb_len1**2 - (dist/2)**2))

        if dist > 0:
            nx = -dy / dist
            ny = dx / dist
        else:
            nx, ny = 1, 0

        if flip:
            nx, ny = -nx, -ny

        kx = mid_x + nx * h
        ky = mid_y + ny * h
        return kx, ky

    l_hip_x, l_hip_y = hip_x - 12, hip_y
    r_hip_x, r_hip_y = hip_x + 12, hip_y

    l_knee_x, l_knee_y = calc_knee(l_hip_x, l_hip_y, l_foot_x, l_foot_y, flip=False)
    r_knee_x, r_knee_y = calc_knee(r_hip_x, r_hip_y, r_foot_x, r_foot_y, flip=True)

    skeleton = {
        'head': (int(head_x), int(head_y)),
        'head_r': head_r,
        'neck': (int(neck_x), int(neck_y)),
        'hip': (int(hip_x), int(hip_y)),
        'l_shoulder': (int(l_shoulder_x), int(l_shoulder_y)),
        'l_elbow': (int(l_elbow_x), int(l_elbow_y)),
        'l_hand': (int(l_hand_x), int(l_hand_y)),
        'r_shoulder': (int(r_shoulder_x), int(r_shoulder_y)),
        'r_elbow': (int(r_elbow_x), int(r_elbow_y)),
        'r_hand': (int(r_hand_x), int(r_hand_y)),
        'l_hip': (int(l_hip_x), int(l_hip_y)),
        'l_knee': (int(l_knee_x), int(l_knee_y)),
        'l_foot': (int(l_foot_x), int(l_foot_y)),
        'r_hip': (int(r_hip_x), int(r_hip_y)),
        'r_knee': (int(r_knee_x), int(r_knee_y)),
        'r_foot': (int(r_foot_x), int(r_foot_y)),
    }
    return skeleton

def draw_stickman(img, skel, frame_num):
    # Glow effect behind stick man
    glow_img = img.copy()
    thickness = 8
    glow_color = (255, 255, 255)
    line_color = (240, 240, 240)
    joint_color = (255, 200, 50) # Glowing gold joints

    # Head
    cv2.circle(img, skel['head'], skel['head_r'], line_color, thickness, cv2.LINE_AA)
    # White fill inside head
    cv2.circle(img, skel['head'], skel['head_r'] - 4, (20, 20, 30), -1, cv2.LINE_AA)

    # Face details (cool sunglasses & smile)
    hx, hy = skel['head']
    # Sunglasses
    cv2.rectangle(img, (hx - 18, hy - 8), (hx + 18, hy + 4), (255, 255, 255), -1, cv2.LINE_AA)
    cv2.rectangle(img, (hx - 16, hy - 6), (hx - 2, hy + 2), (10, 10, 10), -1, cv2.LINE_AA)
    cv2.rectangle(img, (hx + 2, hy - 6), (hx + 16, hy + 2), (10, 10, 10), -1, cv2.LINE_AA)
    # Big Smile
    cv2.ellipse(img, (hx, hy + 8), (10, 8), 0, 0, 180, (255, 255, 255), 2, cv2.LINE_AA)

    # Torso
    cv2.line(img, skel['neck'], skel['hip'], line_color, thickness + 2, cv2.LINE_AA)

    # Arms
    cv2.line(img, skel['l_shoulder'], skel['l_elbow'], line_color, thickness, cv2.LINE_AA)
    cv2.line(img, skel['l_elbow'], skel['l_hand'], line_color, thickness, cv2.LINE_AA)

    cv2.line(img, skel['r_shoulder'], skel['r_elbow'], line_color, thickness, cv2.LINE_AA)
    cv2.line(img, skel['r_elbow'], skel['r_hand'], line_color, thickness, cv2.LINE_AA)

    # Legs
    cv2.line(img, skel['l_hip'], skel['l_knee'], line_color, thickness, cv2.LINE_AA)
    cv2.line(img, skel['l_knee'], skel['l_foot'], line_color, thickness, cv2.LINE_AA)

    cv2.line(img, skel['r_hip'], skel['r_knee'], line_color, thickness, cv2.LINE_AA)
    cv2.line(img, skel['r_knee'], skel['r_foot'], line_color, thickness, cv2.LINE_AA)

    # Joints circles
    joints = [
        skel['neck'], skel['hip'],
        skel['l_shoulder'], skel['l_elbow'], skel['l_hand'],
        skel['r_shoulder'], skel['r_elbow'], skel['r_hand'],
        skel['l_hip'], skel['l_knee'], skel['l_foot'],
        skel['r_hip'], skel['r_knee'], skel['r_foot']
    ]
    for j in joints:
        cv2.circle(img, j, 6, joint_color, -1, cv2.LINE_AA)

    # Musical notes floating around stick man
    t = frame_num / FPS
    notes = ["♪", "♫", "♩", "♬"]
    for i in range(5):
        note_t = (t + i * 0.4) % 2.0
        nx = int(skel['head'][0] + math.sin(note_t * math.pi * 2 + i) * (80 + i * 20))
        ny = int(skel['head'][1] - note_t * 80 - (i * 15))
        alpha = max(0, 1.0 - note_t / 2.0)
        if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
            cv2.putText(img, notes[i % len(notes)], (nx, ny),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (int(255 * alpha), int(220 * alpha), int(100 * alpha)), 2, cv2.LINE_AA)

    return img

def main():
    print(f"Generating Stick Man Dancing Video ({WIDTH}x{HEIGHT} @ {FPS}fps, {DURATION}s)...")

    writer = imageio.get_writer(OUTPUT_FILE, fps=FPS, codec='libx264', quality=8)

    for frame_num in range(TOTAL_FRAMES):
        # Create base scene frame (BGR format in OpenCV)
        frame = create_background(frame_num)

        # Get stickman pose for current frame
        skel = get_stickman_pose(frame_num)

        # Render stickman onto frame
        frame = draw_stickman(frame, skel, frame_num)

        # Convert BGR (OpenCV) to RGB (ImageIO)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        writer.append_data(frame_rgb)

        if (frame_num + 1) % 30 == 0:
            print(f"  Processed {frame_num + 1}/{TOTAL_FRAMES} frames...")

    writer.close()
    print(f"Successfully generated {OUTPUT_FILE}!")

if __name__ == "__main__":
    main()
