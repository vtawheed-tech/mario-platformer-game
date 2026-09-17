import math
import cairo
import numpy as np
import moviepy as mp

WIDTH = 1280
HEIGHT = 720
FPS = 30
DURATION = 30 # seconds
TOTAL_FRAMES = DURATION * FPS

def draw_sky(ctx, t):
    # Sunset sky gradient
    grad = cairo.LinearGradient(0, 0, 0, HEIGHT * 0.7)
    grad.add_color_stop_rgb(0, 0.85, 0.35, 0.1)   # Rich deep orange red top
    grad.add_color_stop_rgb(0.5, 0.95, 0.55, 0.15)  # Warm orange-gold
    grad.add_color_stop_rgb(1, 1.0, 0.8, 0.35)    # Bright golden horizon
    ctx.set_source(grad)
    ctx.rectangle(0, 0, WIDTH, HEIGHT)
    ctx.fill()

    # Sun with radial glow
    sun_x = WIDTH * 0.75 - t * 2.0
    sun_y = HEIGHT * 0.38 + t * 1.5
    sun_rad = cairo.RadialGradient(sun_x, sun_y, 10, sun_x, sun_y, 140)
    sun_rad.add_color_stop_rgba(0, 1.0, 0.95, 0.7, 0.95)
    sun_rad.add_color_stop_rgba(0.2, 1.0, 0.7, 0.2, 0.6)
    sun_rad.add_color_stop_rgba(1, 1.0, 0.5, 0.1, 0.0)
    ctx.set_source(sun_rad)
    ctx.arc(sun_x, sun_y, 140, 0, 2 * math.pi)
    ctx.fill()

    # Sun core
    ctx.set_source_rgb(1.0, 0.98, 0.85)
    ctx.arc(sun_x, sun_y, 35, 0, 2 * math.pi)
    ctx.fill()

def draw_clouds(ctx, t):
    # Drifting warm clouds
    clouds = [
        (100, 120, 160, 30, 0.25),
        (450, 90, 220, 35, 0.20),
        (850, 150, 190, 28, 0.22),
        (1100, 80, 140, 25, 0.18),
    ]
    for cx, cy, rx, ry, alpha in clouds:
        x = (cx - t * 12) % (WIDTH + 300) - 150
        ctx.save()
        grad = cairo.RadialGradient(x, cy, ry*0.2, x, cy, rx)
        grad.add_color_stop_rgba(0, 1.0, 0.75, 0.5, alpha)
        grad.add_color_stop_rgba(1, 0.9, 0.45, 0.2, 0)
        ctx.set_source(grad)
        ctx.scale(1.0, ry / rx)
        ctx.arc(x, cy * (rx / ry), rx, 0, 2 * math.pi)
        ctx.fill()
        ctx.restore()

def draw_birds(ctx, t):
    # V-formation birds flying in distance
    bird_base_x = (WIDTH + 200 - (t * 45)) % (WIDTH + 400) - 100
    bird_base_y = 160 + math.sin(t * 0.8) * 15
    offsets = [(0, 0), (-25, -12), (-50, -22), (-75, -30), (25, -10), (50, -18)]

    ctx.set_source_rgba(0.25, 0.12, 0.05, 0.65)
    ctx.set_line_width(2.0)
    for ox, oy in offsets:
        bx = bird_base_x + ox
        by = bird_base_y + oy
        wing = math.sin(t * 8 + ox * 0.1) * 8
        ctx.move_to(bx - 10, by - wing * 0.5)
        ctx.curve_to(bx - 5, by - wing, bx, by, bx, by)
        ctx.curve_to(bx + 5, by - wing, bx + 10, by - wing * 0.5, bx + 10, by - wing * 0.5)
        ctx.stroke()

def draw_mountains(ctx, scroll_x):
    # Far mountain silhouette (seamless scrolling)
    ctx.set_source_rgb(0.55, 0.26, 0.15)
    pts = [(0, 420), (180, 370), (360, 430), (540, 350), (720, 410), (900, 360), (1080, 420), (1280, 380), (1440, 420)]
    width_span = 1440
    offset = (scroll_x * 0.1) % width_span

    for k in range(-1, 2):
        ctx.save()
        ctx.translate(k * width_span - offset, 0)
        ctx.move_to(-100, HEIGHT)
        for x, y in pts:
            ctx.line_to(x, y)
        ctx.line_to(width_span + 100, HEIGHT)
        ctx.close_path()
        ctx.fill()
        ctx.restore()

    # Mid hills gradient layer (seamless scrolling)
    grad = cairo.LinearGradient(0, 400, 0, HEIGHT)
    grad.add_color_stop_rgb(0, 0.75, 0.40, 0.15)
    grad.add_color_stop_rgb(1, 0.88, 0.50, 0.18)
    ctx.set_source(grad)
    pts2 = [(0, 460), (220, 425), (450, 465), (680, 420), (900, 455), (1120, 430), (1350, 460), (1440, 440)]
    offset2 = (scroll_x * 0.25) % width_span

    for k in range(-1, 2):
        ctx.save()
        ctx.translate(k * width_span - offset2, 0)
        ctx.move_to(-100, HEIGHT)
        for x, y in pts2:
            ctx.line_to(x, y)
        ctx.line_to(width_span + 100, HEIGHT)
        ctx.close_path()
        ctx.fill()
        ctx.restore()

def draw_acacia_tree(ctx, tx, ty, scale=1.0):
    ctx.save()
    ctx.translate(tx, ty)
    ctx.scale(scale, scale)

    # Trunk silhouette / dark warm brown
    ctx.set_source_rgb(0.22, 0.10, 0.05)

    # Main trunk
    ctx.move_to(-12, 0)
    ctx.curve_to(-10, -60, -25, -120, -40, -170)
    ctx.line_to(-25, -170)
    ctx.curve_to(-10, -120, 5, -60, 12, 0)
    ctx.close_path()
    ctx.fill()

    # Major Branches
    branches = [
        (-32, -150, -90, -220, -140, -240),
        (-30, -160, -40, -210, -60, -250),
        (-5, -165, 30, -215, 70, -245),
        (0, -155, 60, -195, 110, -220)
    ]
    for bx1, by1, bx2, by2, bx3, by3 in branches:
        ctx.move_to(bx1, by1)
        ctx.curve_to((bx1+bx2)/2, (by1+by2)/2, bx2, by2, bx3, by3)
        ctx.set_line_width(8)
        ctx.stroke()

        # Flat canopy tops (characteristic Acacia shape)
        ctx.save()
        ctx.translate(bx3, by3)
        grad = cairo.RadialGradient(0, 0, 10, 0, 0, 65)
        grad.add_color_stop_rgb(0, 0.18, 0.10, 0.04)
        grad.add_color_stop_rgb(0.8, 0.25, 0.13, 0.05)
        grad.add_color_stop_rgb(1, 0.35, 0.18, 0.06)
        ctx.set_source(grad)

        ctx.scale(2.2, 0.5)
        ctx.arc(0, 0, 32, 0, 2 * math.pi)
        ctx.fill()
        ctx.restore()

    ctx.restore()

def draw_savanna_ground(ctx, scroll_x):
    # Savanna terrain base layer
    grad = cairo.LinearGradient(0, 480, 0, HEIGHT)
    grad.add_color_stop_rgb(0, 0.88, 0.52, 0.16)   # Golden orange
    grad.add_color_stop_rgb(0.4, 0.78, 0.42, 0.12)  # Warm soil brown
    grad.add_color_stop_rgb(1.0, 0.55, 0.28, 0.08)  # Deep foreground earth
    ctx.set_source(grad)
    ctx.rectangle(0, 480, WIDTH, HEIGHT - 480)
    ctx.fill()

def draw_grass_tufts(ctx, t, scroll_x):
    # Animated blowing tall grass along foreground
    num_tufts = 60
    ctx.set_line_width(2.5)
    for i in range(num_tufts):
        gx = (i * 25 - scroll_x * 0.9) % (WIDTH + 100) - 50
        gy = 520 + (i % 7) * 25
        wind = math.sin(t * 3.5 + i * 0.5) * 15 + math.cos(t * 2.0 + i) * 8

        # Color variety for grass
        if i % 3 == 0:
            ctx.set_source_rgb(0.82, 0.55, 0.15)
        elif i % 3 == 1:
            ctx.set_source_rgb(0.70, 0.42, 0.10)
        else:
            ctx.set_source_rgb(0.90, 0.65, 0.20)

        for b in range(5):
            angle_offset = (b - 2) * 6
            blade_h = 25 + (b % 3) * 10
            ctx.move_to(gx, gy)
            ctx.curve_to(gx + angle_offset*0.5, gy - blade_h*0.5,
                         gx + angle_offset + wind, gy - blade_h,
                         gx + angle_offset * 1.5 + wind * 1.2, gy - blade_h * 1.1)
            ctx.stroke()

def draw_lion(ctx, x, y, t, walk_speed=1.0, is_paused=False):
    ctx.save()
    ctx.translate(x, y)

    # Scale factor for lion
    scale = 0.85
    ctx.scale(scale, scale)

    # Walk cycle kinematics
    phase = t * 7.5 * walk_speed
    if is_paused:
        # Stationary pose during pause
        leg_fl_angle = 0.0
        leg_fr_angle = 0.0
        leg_bl_angle = 0.0
        leg_br_angle = 0.0
        body_bob = 0.0
        head_turn = math.sin((t - 12) * 1.2) * 12 # Head turns towards viewer
        head_lift = -8 + math.sin((t - 12) * 0.8) * 5
        tail_swing = math.sin(t * 3.0) * 15
        blinking = (11.8 < (t % 4.5) < 12.0 or 15.2 < (t % 4.5) < 15.4)
    else:
        leg_fl_angle = math.sin(phase) * 0.45
        leg_fr_angle = math.sin(phase + math.pi) * 0.45
        leg_bl_angle = math.sin(phase + math.pi * 0.5) * 0.4
        leg_br_angle = math.sin(phase + math.pi * 1.5) * 0.4
        body_bob = abs(math.sin(phase * 2)) * 6
        head_turn = math.sin(phase) * 3
        head_lift = math.cos(phase * 2) * 3
        tail_swing = math.sin(phase * 0.8) * 20
        blinking = (2.5 < (t % 6) < 2.65)

    ctx.translate(0, body_bob)

    # 1. Shadow beneath lion
    ctx.save()
    shadow_grad = cairo.RadialGradient(0, 120, 10, 0, 120, 110)
    shadow_grad.add_color_stop_rgba(0, 0, 0, 0, 0.5)
    shadow_grad.add_color_stop_rgba(1, 0, 0, 0, 0)
    ctx.set_source(shadow_grad)
    ctx.scale(1.8, 0.35)
    ctx.arc(0, 120 / 0.35, 80, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()

    # Colors
    LION_BODY = (0.86, 0.58, 0.22)
    LION_BODY_DARK = (0.72, 0.45, 0.15)
    LION_BELLY = (0.94, 0.76, 0.45)
    MANE_DARK = (0.35, 0.16, 0.05)
    MANE_MID = (0.58, 0.28, 0.08)
    MANE_LIGHT = (0.78, 0.45, 0.15)

    # Helper function to draw leg
    def draw_leg(angle, is_back_leg, offset_x):
        ctx.save()
        ctx.translate(offset_x, 30)
        ctx.rotate(angle)

        # Upper leg / thigh
        if is_back_leg:
            ctx.set_source_rgb(*LION_BODY_DARK)
        else:
            ctx.set_source_rgb(*LION_BODY)

        ctx.move_to(-16, -10)
        ctx.curve_to(-20, 20, -15, 50, -10, 70)
        ctx.line_to(10, 70)
        ctx.curve_to(15, 40, 18, 10, 14, -10)
        ctx.close_path()
        ctx.fill()

        # Lower leg & Paw
        ctx.translate(-2, 65)
        knee_angle = -math.sin(phase if not is_paused else 0) * 0.2 if is_back_leg else math.cos(phase if not is_paused else 0) * 0.2
        ctx.rotate(knee_angle)

        ctx.move_to(-9, 0)
        ctx.line_to(-7, 45)
        # Paw
        ctx.curve_to(-12, 48, -14, 52, 10, 52)
        ctx.curve_to(12, 45, 10, 40, 7, 45)
        ctx.line_to(7, 0)
        ctx.close_path()
        ctx.fill()

        ctx.restore()

    # 2. Back legs (drawn behind body)
    draw_leg(leg_bl_angle, True, -90)  # Back Left
    draw_leg(leg_fl_angle, False, 75)   # Front Left

    # 3. Tail
    ctx.save()
    ctx.translate(-120, -15)
    ctx.set_line_width(9)
    ctx.set_source_rgb(*LION_BODY_DARK)
    ctx.move_to(0, 0)
    ctx.curve_to(-40, -10, -70, 20 + tail_swing * 0.5, -60, 60 + tail_swing)
    ctx.stroke()
    # Tail tuft (dark tip)
    ctx.set_source_rgb(*MANE_DARK)
    ctx.arc(-60, 60 + tail_swing, 14, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()

    # 4. Main Body (Torso & Flank)
    ctx.save()
    body_grad = cairo.LinearGradient(0, -60, 0, 60)
    body_grad.add_color_stop_rgb(0, *LION_BODY)
    body_grad.add_color_stop_rgb(0.7, *LION_BODY_DARK)
    body_grad.add_color_stop_rgb(1.0, *LION_BELLY)
    ctx.set_source(body_grad)

    ctx.move_to(-120, 10)
    ctx.curve_to(-130, -35, -90, -65, -20, -60)  # Back curve
    ctx.curve_to(40, -58, 80, -45, 100, -20)    # Shoulder transition
    ctx.curve_to(110, 20, 80, 50, 40, 52)       # Chest curve
    ctx.curve_to(-30, 55, -80, 50, -120, 10)     # Belly curve
    ctx.close_path()
    ctx.fill()
    ctx.restore()

    # 5. Front Legs (drawn in front of body)
    draw_leg(leg_br_angle, True, -70)  # Back Right
    draw_leg(leg_fr_angle, False, 95)  # Front Right

    # 6. Magnificent Mane (Layered vectors with wind animation)
    ctx.save()
    ctx.translate(90 + head_turn * 0.3, -35 + head_lift)

    wind_mane = math.sin(t * 4.0) * 6

    # Mane Layer 1 (Dark back depth)
    ctx.set_source_rgb(*MANE_DARK)
    for a in range(0, 360, 30):
        rad = math.radians(a)
        r = 75 + math.sin(a * 4 + t * 2) * 10
        mx = math.cos(rad) * r - wind_mane * 0.8
        my = math.sin(rad) * r
        ctx.arc(mx, my, 28, 0, 2 * math.pi)
        ctx.fill()

    # Mane Layer 2 (Mid warm tone)
    ctx.set_source_rgb(*MANE_MID)
    for a in range(15, 375, 30):
        rad = math.radians(a)
        r = 62 + math.cos(a * 3) * 8
        mx = math.cos(rad) * r - wind_mane * 0.5
        my = math.sin(rad) * r
        ctx.arc(mx, my, 24, 0, 2 * math.pi)
        ctx.fill()

    # Mane Layer 3 (Foreground golden highlights)
    ctx.set_source_rgb(*MANE_LIGHT)
    for a in range(0, 360, 45):
        rad = math.radians(a)
        r = 50 + math.sin(a * 5) * 6
        mx = math.cos(rad) * r
        my = math.sin(rad) * r
        ctx.arc(mx, my, 20, 0, 2 * math.pi)
        ctx.fill()

    # 7. Lion Head & Face Details
    ctx.save()
    ctx.translate(15 + head_turn, -5)

    # Ears
    ctx.set_source_rgb(*LION_BODY)
    ctx.arc(-22, -35, 14, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_source_rgb(*MANE_DARK)
    ctx.arc(-22, -35, 8, 0, 2 * math.pi)
    ctx.fill()

    # Face Structure
    face_grad = cairo.LinearGradient(-20, -30, 35, 30)
    face_grad.add_color_stop_rgb(0, *LION_BODY)
    face_grad.add_color_stop_rgb(1, *LION_BELLY)
    ctx.set_source(face_grad)
    ctx.move_to(-25, -25)
    ctx.curve_to(0, -40, 30, -30, 42, -5)
    ctx.curve_to(50, 15, 35, 35, 15, 35)
    ctx.curve_to(-15, 35, -30, 10, -25, -25)
    ctx.close_path()
    ctx.fill()

    # Muzzle / Snout
    ctx.set_source_rgb(0.96, 0.88, 0.72)
    ctx.arc(28, 10, 16, 0, 2 * math.pi)
    ctx.fill()

    # Nose
    ctx.set_source_rgb(0.20, 0.10, 0.08)
    ctx.move_to(36, 2)
    ctx.line_to(44, 2)
    ctx.line_to(40, 10)
    ctx.close_path()
    ctx.fill()

    # Mouth line
    ctx.set_line_width(2.5)
    ctx.move_to(40, 10)
    ctx.curve_to(38, 18, 32, 20, 26, 17)
    ctx.stroke()

    # Eyes
    if blinking:
        ctx.set_source_rgb(0.2, 0.1, 0.05)
        ctx.set_line_width(3.0)
        ctx.move_to(12, -8)
        ctx.line_to(24, -6)
        ctx.stroke()
    else:
        # Amber Eye
        ctx.set_source_rgb(0.95, 0.75, 0.10)
        ctx.arc(18, -8, 6.5, 0, 2 * math.pi)
        ctx.fill()
        # Pupil
        ctx.set_source_rgb(0.05, 0.02, 0.0)
        ctx.arc(19, -8, 3.2, 0, 2 * math.pi)
        ctx.fill()
        # Eye highlight
        ctx.set_source_rgb(1.0, 1.0, 1.0)
        ctx.arc(17.5, -9.5, 1.5, 0, 2 * math.pi)
        ctx.fill()

    # Whiskers
    ctx.set_source_rgba(0.95, 0.90, 0.80, 0.7)
    ctx.set_line_width(1.2)
    whiskers = [(34, 10, 60, 5), (34, 12, 62, 14), (34, 14, 58, 22)]
    for wx1, wy1, wx2, wy2 in whiskers:
        ctx.move_to(wx1, wy1)
        ctx.line_to(wx2, wy2)
        ctx.stroke()

    ctx.restore() # End face
    ctx.restore() # End mane
    ctx.restore() # End lion

def render_frame(t):
    # Setup Cairo surface & context
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    ctx = cairo.Context(surface)

    # Camera panning logic across 30 seconds
    # Phase 1: t=0..12 - Lion walks across savanna left-to-right
    # Phase 2: t=12..17 - Lion stops, looks around gracefully, wind in mane
    # Phase 3: t=17..30 - Lion continues walking into the golden horizon

    if t < 12.0:
        is_paused = False
        lion_progress = t / 12.0
        lion_x = 180 + lion_progress * 420
        scroll_x = t * 35.0
        walk_speed = 1.0
    elif t < 17.0:
        is_paused = True
        lion_x = 600
        scroll_x = 12.0 * 35.0
        walk_speed = 0.0
    else:
        is_paused = False
        lion_progress = (t - 17.0) / 13.0
        lion_x = 600 + lion_progress * 480
        scroll_x = 12.0 * 35.0 + (t - 17.0) * 35.0
        walk_speed = 1.0

    lion_y = 510

    # Draw Scene Layers
    draw_sky(ctx, t)
    draw_clouds(ctx, t)
    draw_birds(ctx, t)
    draw_mountains(ctx, scroll_x)

    # Midground Acacia trees
    draw_acacia_tree(ctx, (250 - scroll_x * 0.4) % (WIDTH + 400) - 200, 480, scale=0.55)
    draw_acacia_tree(ctx, (850 - scroll_x * 0.45) % (WIDTH + 400) - 200, 470, scale=0.75)
    draw_acacia_tree(ctx, (1400 - scroll_x * 0.5) % (WIDTH + 400) - 200, 490, scale=0.65)

    draw_savanna_ground(ctx, scroll_x)

    # Foreground Acacia tree close by
    draw_acacia_tree(ctx, (1100 - scroll_x * 0.7) % (WIDTH + 600) - 300, 510, scale=1.1)

    # The Hero Lion
    draw_lion(ctx, lion_x, lion_y, t, walk_speed=walk_speed, is_paused=is_paused)

    # Foreground grass blowing in wind
    draw_grass_tufts(ctx, t, scroll_x)

    # Extract BGRA image buffer from Cairo and convert to RGB numpy array for MoviePy
    buf = surface.get_data()
    img = np.frombuffer(buf, np.uint8).reshape((HEIGHT, WIDTH, 4))
    # Cairo FORMAT_ARGB32 is BGRA in memory on x86_64
    rgb_img = img[:, :, [2, 1, 0]]
    return rgb_img

def main():
    print("Generating 30s Lion Savanna Animation (1280x720 16:9)...")
    clip = mp.VideoClip(render_frame, duration=DURATION)
    clip.write_videofile(
        "lion_savanna.mp4",
        fps=FPS,
        codec="libx264",
        ffmpeg_params=["-pix_fmt", "yuv420p"]
    )
    print("Animation successfully generated: lion_savanna.mp4")

if __name__ == "__main__":
    main()
