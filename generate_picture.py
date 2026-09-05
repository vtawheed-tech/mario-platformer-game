import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps

WIDTH = 3840
HEIGHT = 2160

def generate_ww2_sniper_art():
    print(f"Generating 4K picture ({WIDTH}x{HEIGHT}, 16:9 ratio)...")
    np.random.seed(42)
    random.seed(42)

    # 1. Base Canvas - Dramatic Twilight / Dawn Sky Gradient
    sky = np.zeros((HEIGHT, WIDTH, 3), dtype=np.float32)

    # Gradient from dark stormy blue-gray at top to warm amber/orange horizon
    y_coords = np.linspace(0, 1, HEIGHT)[:, None]

    top_color = np.array([20, 28, 45], dtype=np.float32)      # Deep night blue
    mid_color = np.array([80, 60, 75], dtype=np.float32)      # Dusk purple/slate
    horizon_color = np.array([220, 110, 40], dtype=np.float32) # Fiery war-torn horizon
    bottom_color = np.array([35, 30, 28], dtype=np.float32)   # Dark muddy terrain base

    for y in range(HEIGHT):
        ratio = y / HEIGHT
        if ratio < 0.45:
            factor = ratio / 0.45
            c = (1 - factor) * top_color + factor * mid_color
        elif ratio < 0.65:
            factor = (ratio - 0.45) / 0.20
            c = (1 - factor) * mid_color + factor * horizon_color
        else:
            factor = (ratio - 0.65) / 0.35
            c = (1 - factor) * horizon_color + factor * bottom_color
        sky[y, :] = c

    base_img = Image.fromarray(np.uint8(sky))

    # Add cloud noise layer
    noise_small = np.random.normal(128, 40, (HEIGHT // 8, WIDTH // 8, 3))
    noise_img = Image.fromarray(np.uint8(np.clip(noise_small, 0, 255)))
    noise_img = noise_img.resize((WIDTH, HEIGHT), Image.Resampling.BILINEAR)
    noise_img = noise_img.filter(ImageFilter.GaussianBlur(30))
    base_img = Image.blend(base_img, noise_img, 0.15)

    draw = ImageDraw.Draw(base_img, "RGBA")

    # 2. Distant Mountains and Ruined City Skyline
    # Mountain layer 1 (Far background)
    mtn_pts_1 = [(0, HEIGHT * 0.6)]
    for x in range(0, WIDTH + 100, 100):
        h = HEIGHT * 0.52 + math.sin(x * 0.002) * 120 + math.cos(x * 0.005) * 80 + random.randint(-20, 20)
        mtn_pts_1.append((x, h))
    mtn_pts_1.append((WIDTH, HEIGHT))
    mtn_pts_1.append((0, HEIGHT))
    draw.polygon(mtn_pts_1, fill=(40, 45, 55, 230))

    # Distant ruined buildings / tree silhouettes
    mtn_pts_2 = [(0, HEIGHT * 0.65)]
    for x in range(0, WIDTH + 40, 40):
        # Create silhouette spikes resembling destroyed structures / burnt pine trees
        if random.random() < 0.3:
            h = HEIGHT * 0.55 - random.randint(40, 160)
        else:
            h = HEIGHT * 0.58 + math.sin(x * 0.008) * 60
        mtn_pts_2.append((x, h))
    mtn_pts_2.append((WIDTH, HEIGHT))
    mtn_pts_2.append((0, HEIGHT))
    draw.polygon(mtn_pts_2, fill=(25, 28, 32, 240))

    # Fog / haze over background
    fog = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    fog_draw = ImageDraw.Draw(fog)
    for y in range(int(HEIGHT * 0.45), int(HEIGHT * 0.75)):
        alpha = int(120 * math.sin((y - HEIGHT * 0.45) / (HEIGHT * 0.3) * math.pi))
        fog_draw.line([(0, y), (WIDTH, y)], fill=(210, 160, 120, alpha))
    fog = fog.filter(ImageFilter.GaussianBlur(40))
    base_img = Image.alpha_composite(base_img.convert("RGBA"), fog)

    # Re-obtain draw object on composite image
    draw = ImageDraw.Draw(base_img, "RGBA")

    # 3. Midground: Ruined Bunker / Wall / Trench Rocks (Left side to Center)
    wall_pts = [
        (0, HEIGHT * 0.50),
        (WIDTH * 0.35, HEIGHT * 0.52),
        (WIDTH * 0.40, HEIGHT * 0.68),
        (WIDTH * 0.45, HEIGHT * 0.85),
        (WIDTH * 0.45, HEIGHT),
        (0, HEIGHT)
    ]
    draw.polygon(wall_pts, fill=(30, 32, 35, 255))

    # Brick & Concrete Texture on Wall
    for _ in range(800):
        rx = random.randint(0, int(WIDTH * 0.42))
        ry = random.randint(int(HEIGHT * 0.52), HEIGHT)
        rw = random.randint(20, 80)
        rh = random.randint(10, 30)
        shade = random.randint(20, 50)
        draw.rectangle([rx, ry, rx + rw, ry + rh], fill=(shade, shade + 2, shade + 5, 180), outline=(15, 15, 18, 200))

    # Snow & Debris on the Wall
    for _ in range(400):
        sx = random.randint(0, int(WIDTH * 0.42))
        sy = random.randint(int(HEIGHT * 0.50), HEIGHT)
        sw = random.randint(15, 60)
        draw.ellipse([sx, sy, sx + sw, sy + random.randint(3, 8)], fill=(210, 215, 225, 160))

    # 4. Foreground Subject: WW2 Sniper in Ghillie/Winter Camo aiming down scope
    # Sniper Position: Lower-right to center-right area, crouching/prone behind cover

    # Body Silhouette & Uniform Layers
    body_center_x = int(WIDTH * 0.62)
    body_center_y = int(HEIGHT * 0.72)

    # Lower Body / Coat (Olive Drab / Winter Camo Greens & Browns)
    draw.ellipse([body_center_x - 500, body_center_y - 100, body_center_x + 400, body_center_y + 600], fill=(45, 52, 40, 255)) # Torso base
    draw.polygon([
        (body_center_x - 550, HEIGHT),
        (body_center_x - 300, body_center_y - 80),
        (body_center_x + 500, body_center_y + 100),
        (WIDTH, HEIGHT)
    ], fill=(38, 44, 35, 255))

    # Ghillie burlap strands & camo texture on coat/shoulders
    colors = [(55, 62, 42), (40, 48, 32), (70, 65, 48), (85, 78, 55), (30, 35, 25), (180, 175, 160)]
    for _ in range(2500):
        gx = random.randint(body_center_x - 550, WIDTH)
        gy = random.randint(body_center_y - 200, HEIGHT)
        length = random.randint(15, 50)
        angle = random.uniform(-math.pi / 3, math.pi / 3)
        ex = gx + int(length * math.sin(angle))
        ey = gy + int(length * math.cos(angle))
        c = random.choice(colors)
        draw.line([(gx, gy), (ex, ey)], fill=c + (230,), width=random.randint(3, 7))

    # Helmet with Cloth Cover & Camo Netting
    helmet_x = body_center_x - 120
    helmet_y = body_center_y - 220
    draw.ellipse([helmet_x - 140, helmet_y - 100, helmet_x + 140, helmet_y + 70], fill=(50, 56, 45, 255))
    # Helmet strap & shadow
    draw.arc([helmet_x - 142, helmet_y - 102, helmet_x + 142, helmet_y + 72], 180, 360, fill=(25, 28, 22, 255), width=8)
    # Camo net grid on helmet
    for hx in range(helmet_x - 130, helmet_x + 130, 20):
        draw.line([(hx, helmet_y - 80), (hx + 30, helmet_y + 50)], fill=(30, 35, 25, 200), width=3)
        draw.line([(hx + 30, helmet_y - 80), (hx, helmet_y + 50)], fill=(30, 35, 25, 200), width=3)

    # Face / Balaclava / Eyes focused forward
    draw.ellipse([helmet_x - 80, helmet_y + 10, helmet_x + 60, helmet_y + 130], fill=(35, 32, 30, 255)) # Dark camo mask
    # Eye slice revealing intense sniper gaze
    draw.rectangle([helmet_x - 50, helmet_y + 35, helmet_x + 30, helmet_y + 60], fill=(185, 145, 120, 255))
    # Eyes
    draw.ellipse([helmet_x - 35, helmet_y + 42, helmet_x - 15, helmet_y + 54], fill=(240, 240, 245, 255))
    draw.ellipse([helmet_x - 28, helmet_y + 44, helmet_x - 20, helmet_y + 52], fill=(40, 65, 80, 255)) # Pupil focused left towards rifle scope
    draw.ellipse([helmet_x + 2, helmet_y + 42, helmet_x + 22, helmet_y + 54], fill=(240, 240, 245, 255))
    draw.ellipse([helmet_x + 8, helmet_y + 44, helmet_x + 16, helmet_y + 52], fill=(40, 65, 80, 255))

    # 5. WW2 Bolt-Action Sniper Rifle with High-Precision Optics
    # Rifle barrel and stock angled towards target (left-center)
    # Rifle Start: (WIDTH * 0.22, HEIGHT * 0.56) to (WIDTH * 0.75, HEIGHT * 0.75)

    rifle_start = (int(WIDTH * 0.18), int(HEIGHT * 0.55))
    rifle_end = (int(WIDTH * 0.78), int(HEIGHT * 0.76))

    # Wooden Stock (Rich Walnut / Oak texture)
    draw.line([rifle_start, rifle_end], fill=(75, 42, 22, 255), width=38)
    draw.line([rifle_start, rifle_end], fill=(110, 62, 32, 255), width=24)
    draw.line([rifle_start, rifle_end], fill=(50, 28, 14, 255), width=10)

    # Steel Barrel (Gunmetal Gray with metallic highlight)
    barrel_start = (int(WIDTH * 0.12), int(HEIGHT * 0.53))
    barrel_end = (int(WIDTH * 0.65), int(HEIGHT * 0.71))
    draw.line([barrel_start, barrel_end], fill=(35, 38, 42, 255), width=22)
    draw.line([barrel_start, barrel_end], fill=(85, 92, 100, 255), width=8) # Metallic highlight line
    draw.line([barrel_start, barrel_end], fill=(15, 18, 22, 255), width=4)  # Shadow line

    # Rifle Muzzle & Front Sight Piece
    muzzle_pos = barrel_start
    draw.rectangle([muzzle_pos[0] - 15, muzzle_pos[1] - 15, muzzle_pos[0] + 15, muzzle_pos[1] + 15], fill=(25, 28, 30, 255))
    draw.polygon([
        (muzzle_pos[0], muzzle_pos[1] - 30),
        (muzzle_pos[0] - 8, muzzle_pos[1] - 10),
        (muzzle_pos[0] + 8, muzzle_pos[1] - 10)
    ], fill=(20, 22, 25, 255)) # Front sight blade

    # Bolt Mechanism & Receiver Assembly
    receiver_x = int(WIDTH * 0.52)
    receiver_y = int(HEIGHT * 0.66)
    draw.rectangle([receiver_x - 60, receiver_y - 25, receiver_x + 80, receiver_y + 25], fill=(28, 30, 35, 255))
    # Bolt handle
    draw.line([(receiver_x + 20, receiver_y), (receiver_x + 50, receiver_y + 40)], fill=(70, 75, 82, 255), width=12)
    draw.ellipse([receiver_x + 42, receiver_y + 35, receiver_x + 62, receiver_y + 55], fill=(50, 55, 60, 255))

    # Leather Sling wrapped around barrel & stock
    sling_pts = [
        (int(WIDTH * 0.22), int(HEIGHT * 0.58)),
        (int(WIDTH * 0.32), int(HEIGHT * 0.65)),
        (int(WIDTH * 0.48), int(HEIGHT * 0.72)),
        (int(WIDTH * 0.60), int(HEIGHT * 0.73))
    ]
    draw.line(sling_pts, fill=(90, 55, 30, 255), width=10)

    # Gloved Hands holding the Rifle
    # Left hand supporting forward stock
    left_hand_x = int(WIDTH * 0.38)
    left_hand_y = int(HEIGHT * 0.61)
    draw.ellipse([left_hand_x - 45, left_hand_y - 30, left_hand_x + 45, left_hand_y + 35], fill=(30, 35, 28, 255)) # Leather/cloth glove
    draw.arc([left_hand_x - 48, left_hand_y - 32, left_hand_x + 48, left_hand_y + 37], 0, 360, fill=(15, 18, 14, 255), width=4)

    # Right hand on trigger & receiver
    right_hand_x = receiver_x + 10
    right_hand_y = receiver_y + 15
    draw.ellipse([right_hand_x - 40, right_hand_y - 25, right_hand_x + 40, right_hand_y + 35], fill=(32, 38, 30, 255))

    # 6. High-Precision WW2 Telescopic Scope (e.g. PU Scope / Zeiss 4x)
    scope_center_x = int(WIDTH * 0.42)
    scope_center_y = int(HEIGHT * 0.61)
    scope_length = 340
    scope_radius = 42

    # Scope Mounts connected to receiver
    draw.rectangle([scope_center_x - 100, scope_center_y, scope_center_x - 70, scope_center_y + 40], fill=(20, 22, 25, 255))
    draw.rectangle([scope_center_x + 70, scope_center_y, scope_center_x + 100, scope_center_y + 40], fill=(20, 22, 25, 255))

    # Main Scope Tube
    draw.rectangle([scope_center_x - scope_length // 2, scope_center_y - scope_radius,
                    scope_center_x + scope_length // 2, scope_center_y + scope_radius], fill=(22, 25, 28, 255))
    # Metallic reflection / highlight along scope top
    draw.line([(scope_center_x - scope_length // 2, scope_center_y - scope_radius + 4),
               (scope_center_x + scope_length // 2, scope_center_y - scope_radius + 4)], fill=(120, 130, 142, 255), width=6)

    # Scope Adjustment Turrets (Windage & Elevation Knobs)
    draw.rectangle([scope_center_x - 20, scope_center_y - scope_radius - 28, scope_center_x + 20, scope_center_y - scope_radius], fill=(30, 34, 38, 255))
    draw.rectangle([scope_center_x - 15, scope_center_y - scope_radius - 35, scope_center_x + 15, scope_center_y - scope_radius - 28], fill=(50, 55, 62, 255))

    draw.rectangle([scope_center_x - 20, scope_center_y, scope_center_x + 20, scope_center_y + scope_radius + 28], fill=(30, 34, 38, 255))

    # Scope Objective Lens (Front Bell - Facing Left)
    front_lens_x = scope_center_x - scope_length // 2
    draw.ellipse([front_lens_x - 25, scope_center_y - scope_radius - 12,
                  front_lens_x + 25, scope_center_y + scope_radius + 12], fill=(15, 18, 20, 255))

    # Glowing Lens Reflection (Coated Optics Reflection - Cyan/Amber tint)
    lens_overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    lens_draw = ImageDraw.Draw(lens_overlay)
    lens_draw.ellipse([front_lens_x - 20, scope_center_y - scope_radius - 8,
                       front_lens_x + 15, scope_center_y + scope_radius + 8], fill=(40, 180, 220, 140))
    lens_draw.ellipse([front_lens_x - 10, scope_center_y - scope_radius + 5,
                       front_lens_x + 10, scope_center_y + scope_radius - 5], fill=(255, 170, 60, 120))
    # Bright specular glare slant
    lens_draw.polygon([
        (front_lens_x - 15, scope_center_y - 30),
        (front_lens_x + 5, scope_center_y - 35),
        (front_lens_x - 5, scope_center_y + 35),
        (front_lens_x - 20, scope_center_y + 30)
    ], fill=(255, 255, 255, 200))

    base_img = Image.alpha_composite(base_img, lens_overlay)
    draw = ImageDraw.Draw(base_img, "RGBA")

    # Scope Ocular Lens (Rear Eyepiece - Facing Right towards sniper eye)
    rear_lens_x = scope_center_x + scope_length // 2
    draw.ellipse([rear_lens_x - 20, scope_center_y - scope_radius - 6,
                  rear_lens_x + 20, scope_center_y + scope_radius + 6], fill=(25, 28, 32, 255))
    # Rubber eyecup
    draw.ellipse([rear_lens_x + 5, scope_center_y - scope_radius - 10,
                  rear_lens_x + 35, scope_center_y + scope_radius + 10], fill=(15, 15, 18, 255))

    # 7. Cinematic Effects: Muzzle Heat Haze, Dust/Snow Flakes, Sunset Rays, Vignette

    # Floating Snow / Dust Particles
    fx_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    fx_draw = ImageDraw.Draw(fx_layer)

    for _ in range(600):
        px = random.randint(0, WIDTH)
        py = random.randint(0, HEIGHT)
        p_size = random.randint(2, 8)
        p_alpha = random.randint(100, 230)
        fx_draw.ellipse([px, py, px + p_size, py + p_size], fill=(240, 245, 255, p_alpha))

    # Light Rays / Sun Flare from Horizon (Warm Golden Glow from top-left/center)
    flare_center = (int(WIDTH * 0.35), int(HEIGHT * 0.48))
    for i in range(12):
        angle = random.uniform(-math.pi / 4, math.pi / 2)
        ray_length = random.randint(800, 2200)
        end_x = flare_center[0] + int(ray_length * math.cos(angle))
        end_y = flare_center[1] + int(ray_length * math.sin(angle))
        width = random.randint(60, 200)
        fx_draw.polygon([
            flare_center,
            (end_x - width, end_y),
            (end_x + width, end_y)
        ], fill=(255, 180, 90, random.randint(15, 35)))

    # Lens Flare Circles
    for step in range(1, 6):
        fx_x = flare_center[0] + step * 250
        fx_y = flare_center[1] + step * 120
        rad = random.randint(30, 120)
        fx_draw.ellipse([fx_x - rad, fx_y - rad, fx_x + rad, fx_y + rad], fill=(255, 200, 120, 25))

    base_img = Image.alpha_composite(base_img, fx_layer)

    # Vignette Effect (Darkening edges for cinematic depth)
    vignette = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    v_draw = ImageDraw.Draw(vignette)

    # Draw dark radial gradient around edges
    cx, cy = WIDTH // 2, HEIGHT // 2
    max_dist = math.sqrt(cx**2 + cy**2)

    # Efficient block vignette using numpy
    x_grid, y_grid = np.meshgrid(np.arange(WIDTH), np.arange(HEIGHT))
    dist_from_center = np.sqrt((x_grid - cx)**2 + (y_grid - cy)**2)
    norm_dist = np.clip((dist_from_center - max_dist * 0.45) / (max_dist * 0.55), 0, 1)
    vignette_alpha = (norm_dist ** 2 * 210).astype(np.uint8)

    vignette_np = np.zeros((HEIGHT, WIDTH, 4), dtype=np.uint8)
    vignette_np[:, :, 3] = vignette_alpha
    vignette_img = Image.fromarray(vignette_np, "RGBA")

    base_img = Image.alpha_composite(base_img, vignette_img)

    # 8. Post-Processing: Film Grain & Color Contrast Enhancement
    final_rgb = base_img.convert("RGB")

    # Add subtle film grain texture
    grain = np.random.normal(0, 8, (HEIGHT, WIDTH, 3)).astype(np.float32)
    rgb_np = np.array(final_rgb, dtype=np.float32) + grain
    rgb_np = np.clip(rgb_np, 0, 255).astype(np.uint8)

    final_img = Image.fromarray(rgb_np)

    # Contrast & Color Vibrance adjustment
    enhancer = ImageEnhance.Contrast(final_img)
    final_img = enhancer.enhance(1.15)

    color_enhancer = ImageEnhance.Color(final_img)
    final_img = color_enhancer.enhance(1.08)

    sharpness = ImageEnhance.Sharpness(final_img)
    final_img = sharpness.enhance(1.2)

    # Save final 4K image
    output_filename = "ww2_sniper_4k.png"
    final_img.save(output_filename, "PNG", quality=100)
    print(f"Successfully generated 4K image: '{output_filename}' ({WIDTH}x{HEIGHT}).")

if __name__ == "__main__":
    generate_ww2_sniper_art()
