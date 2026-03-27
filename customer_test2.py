"""
=============================================================================
 BeautyReel AI — AI Background Generator (FINAL)

 FLOW:
 1. User provides ANY product image (any angle, tilted, lying, standing)
 2. User types ANY background prompt
 3. FLUX.1 AI generates background image
 4. rembg (isnet model) removes background — product 100% intact
 5. Product placed on AI background — no zoom, no blur, no distortion
 6. moviepy creates professional video with gentle motion
=============================================================================
 Install:
   pip install "rembg[cpu]" moviepy==1.0.3 Pillow numpy requests
=============================================================================
"""

import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from rembg import remove
import io, requests, time
from moviepy.editor import ImageClip, CompositeVideoClip, concatenate_videoclips
from moviepy.video.fx.all import fadein, fadeout, colorx
from moviepy.video.VideoClip import VideoClip
import random

# =============================================================================
#  CONFIGURATION
# =============================================================================

HF_TOKEN      = "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"
OUTPUT_FOLDER = r"Final_reels_videos_dataset\ai_generated_test"
SD_API_URL    = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

TARGET_W = 1080
TARGET_H = 1920

# Very gentle shots — minimal zoom, product always fully visible
SHOTS = [
    {"zoom_s":1.03,"zoom_e":1.00,"px":0.00,  "py":0.00,  "bright":1.04,"label":"REVEAL"},
    {"zoom_s":1.04,"zoom_e":1.02,"px":0.00,  "py":-0.02, "bright":1.04,"label":"SLIGHT UP"},
    {"zoom_s":1.03,"zoom_e":1.03,"px":-0.03, "py":0.00,  "bright":1.04,"label":"LEFT"},
    {"zoom_s":1.03,"zoom_e":1.03,"px": 0.03, "py":0.00,  "bright":1.04,"label":"RIGHT"},
    {"zoom_s":1.04,"zoom_e":1.02,"px":0.00,  "py":0.02,  "bright":1.05,"label":"SLIGHT DOWN"},
    {"zoom_s":1.04,"zoom_e":1.02,"px":0.01,  "py":-0.01, "bright":1.05,"label":"ANGLE"},
    {"zoom_s":1.02,"zoom_e":1.00,"px":0.00,  "py":0.00,  "bright":1.03,"label":"FINALE"},
]

# =============================================================================
#  STEP 1 — User Input
# =============================================================================

def get_user_input():
    print("\n" + "="*60)
    print("  BEAUTYREEL AI — AI Background Video Generator")
    print("  Powered by FLUX.1 + rembg + moviepy")
    print("="*60)

    print("\n  Enter your product image path:")
    print("  (Any product, any angle — tilted, lying, standing)")
    print(r"  Example: images_datasets\lipstick_image_dataset\lipstick.jpg")
    print("-"*60)
    image_path = input("  Image path: ").strip().strip('"')

    while not Path(image_path).exists():
        print(f"  ERROR: File not found — {image_path}")
        print("  Please enter correct path.")
        image_path = input("  Image path: ").strip().strip('"')

    print(f"  Image found: {image_path}\n")

    print("  Enter product name (shown in video):")
    print("  Example: LIPSTICK / LIP PENCIL / CONCEALER / POWDER")
    product_name = input("  Product name: ").strip().upper()
    if not product_name:
        product_name = "PRODUCT"

    print("\n  Enter tagline for video:")
    print("  Example: Bold. Glamorous. Unstoppable")
    tagline = input("  Tagline: ").strip()
    if not tagline:
        tagline = "Beauty Redefined"

    print("\n  Enter background prompt for AI:")
    print("  Examples:")
    print("  - dark burgundy velvet, dramatic studio lighting")
    print("  - soft pink marble, luxury beauty photography")
    print("  - rose gold bokeh, glamour product shot")
    print("  - pure black glossy surface, neon accent light")
    print("  - white marble studio, soft diffused light")
    print("  - golden hour warm glow, outdoor luxury")
    print("-"*60)
    prompt = input("  Your prompt: ").strip()
    while len(prompt) < 3:
        print("  Please enter a prompt.")
        prompt = input("  Your prompt: ").strip()

    full_prompt = (
        f"{prompt}, "
        f"product photography background, high quality, "
        f"8k resolution, professional studio, "
        f"no people, no text, clean background only"
    )

    print(f"\n  Product     : {product_name}")
    print(f"  Tagline     : {tagline}")
    print(f"  Prompt      : {prompt}\n")

    return image_path, product_name, tagline, prompt, full_prompt


# =============================================================================
#  STEP 2 — Generate Background with FLUX.1
# =============================================================================

def generate_background(full_prompt):
    print("  Generating background with FLUX.1 AI...")
    print("  Please wait 30-60 seconds...\n")

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type" : "application/json"
    }
    payload = {
        "inputs": full_prompt,
        "parameters": {
            "width"              : TARGET_W,
            "height"             : TARGET_H,
            "num_inference_steps": 4,
            "guidance_scale"     : 3.5,
        }
    }

    for attempt in range(1, 4):
        try:
            print(f"  Attempt {attempt}/3...")
            response = requests.post(
                SD_API_URL, headers=headers,
                json=payload, timeout=120
            )

            if response.status_code == 200:
                bg_img = Image.open(io.BytesIO(response.content)).convert("RGB")
                bg_img = bg_img.resize((TARGET_W, TARGET_H), Image.LANCZOS)
                print("  Background generated!\n")
                return bg_img

            elif response.status_code == 503:
                print("  Model loading... waiting 30 seconds...")
                time.sleep(30)
            else:
                print(f"  ERROR: {response.status_code} — {response.text[:120]}")
                if attempt < 3:
                    time.sleep(15)

        except requests.exceptions.Timeout:
            print("  Timeout. Retrying...")
            time.sleep(10)
        except Exception as e:
            print(f"  Error: {e}")
            time.sleep(10)

    return None


# =============================================================================
#  STEP 3 — Remove Background (any angle, product 100% intact)
# =============================================================================

def remove_product_bg(image_path):
    """
    Removes background reliably for ANY product image.
    Pre-processes image before removal for better product detection.
    Product shape, angle, color — 100% preserved.
    """
    from PIL import ImageEnhance
    print("  Removing product background...")

    # Step 1: Load original
    original   = Image.open(image_path).convert("RGB")
    orig_w, orig_h = original.size
    print(f"  Original size: {orig_w}x{orig_h}")

    # Step 2: Resize very large images for rembg
    max_side = 1500
    if max(orig_w, orig_h) > max_side:
        ratio    = max_side / max(orig_w, orig_h)
        new_w    = int(orig_w * ratio)
        new_h    = int(orig_h * ratio)
        original = original.resize((new_w, new_h), Image.LANCZOS)
        print(f"  Resized: {new_w}x{new_h}")

    # Step 3: Sharpen + boost contrast BEFORE rembg
    # This helps rembg detect product edges clearly
    enhanced = original
    enhanced = ImageEnhance.Sharpness(enhanced).enhance(2.0)    # sharpen edges
    enhanced = ImageEnhance.Contrast(enhanced).enhance(1.4)     # boost contrast
    enhanced = ImageEnhance.Color(enhanced).enhance(1.2)        # boost color

    # Step 4: Send enhanced image to rembg
    buf = io.BytesIO()
    enhanced.save(buf, format="PNG")
    raw = buf.getvalue()

    removed = remove(raw)
    mask_img = Image.open(io.BytesIO(removed)).convert("RGBA")

    # Step 5: Apply rembg mask to ORIGINAL image (not enhanced)
    # This keeps product colors natural — only background is removed
    if max(orig_w, orig_h) > max_side:
        orig_full = Image.open(image_path).convert("RGB")
    else:
        orig_full = Image.open(image_path).convert("RGB")

    # Resize mask to original size if needed
    if mask_img.size != orig_full.size:
        mask_img = mask_img.resize(orig_full.size, Image.LANCZOS)

    # Extract alpha from rembg result — apply to original image
    _, _, _, alpha_ch = mask_img.split()

    # Gentle alpha smoothing — removes jagged pixels only
    alpha_smooth = alpha_ch.filter(ImageFilter.GaussianBlur(radius=0.4))

    # Final product: original colors + clean mask
    product_img = orig_full.convert("RGBA")
    product_img.putalpha(alpha_smooth)

    print(f"  Background removed — product intact!\n")
    return product_img


def smart_crop_product(product_img):
    """
    Detects actual product pixels regardless of angle.
    Removes only empty transparent border.
    Generous 6% padding — product edges never cut.
    Works for tilted, diagonal, lying products.
    """
    alpha = np.array(product_img)[:, :, 3]
    rows  = np.any(alpha > 5, axis=1)
    cols  = np.any(alpha > 5, axis=0)

    if not rows.any() or not cols.any():
        return product_img

    row_min, row_max = np.where(rows)[0][[0, -1]]
    col_min, col_max = np.where(cols)[0][[0, -1]]

    h, w    = alpha.shape
    pad_x   = int(w * 0.06)   # 6% generous padding
    pad_y   = int(h * 0.06)
    row_min = max(0, row_min - pad_y)
    row_max = min(h, row_max + pad_y)
    col_min = max(0, col_min - pad_x)
    col_max = min(w, col_max + pad_x)

    cropped = product_img.crop((col_min, row_min, col_max, row_max))
    print(f"  Product detected: {cropped.size[0]}x{cropped.size[1]} px")
    return cropped


# =============================================================================
#  STEP 4 — Smart Compose (handles any angle, any orientation)
# =============================================================================

def compose_image(product_img, bg_img):
    """
    Places product on AI background.
    Detects product orientation automatically.
    Product angle, shape, details — 100% preserved.
    No zoom, no distortion, no blur.
    """
    print("  Composing product on AI background...")

    product_img = smart_crop_product(product_img)
    pw, ph      = product_img.size
    aspect      = pw / ph

    bg = bg_img.resize((TARGET_W, TARGET_H), Image.LANCZOS).convert("RGBA")

    print(f"  Detected aspect ratio: {aspect:.2f}")

    # Smart sizing based on product orientation
    # Rule: product must fit fully — never crop any part
    if aspect >= 2.0:
        # Very wide (e.g. open palette, flat brush)
        max_w = TARGET_W * 0.94
        max_h = TARGET_H * 0.42
        print("  Orientation: Very wide product")

    elif aspect >= 1.2:
        # Wide/landscape (e.g. lipstick lying flat, compact)
        max_w = TARGET_W * 0.90
        max_h = TARGET_H * 0.48
        print("  Orientation: Landscape/lying product")

    elif aspect >= 0.75:
        # Square/normal (e.g. powder, concealer, compact)
        max_w = TARGET_W * 0.82
        max_h = TARGET_H * 0.55
        print("  Orientation: Square/normal product")

    elif aspect >= 0.45:
        # Slightly tall (e.g. standing lipstick, foundation)
        max_w = TARGET_W * 0.70
        max_h = TARGET_H * 0.60
        print("  Orientation: Slightly tall product")

    else:
        # Very tall (e.g. lip pencil, mascara, nail polish)
        max_w = TARGET_W * 0.52
        max_h = TARGET_H * 0.65
        print("  Orientation: Tall/vertical product")

    # Calculate scale — preserve aspect ratio strictly
    scale = min(max_w / pw, max_h / ph)

    # Minimum size: product always at least 38% frame width
    min_scale = (TARGET_W * 0.38) / pw
    scale     = max(scale, min_scale)

    # Safety caps — product never goes outside frame
    while int(pw * scale) > int(TARGET_W * 0.96):
        scale *= 0.97
    while int(ph * scale) > int(TARGET_H * 0.67):
        scale *= 0.97

    nw = int(pw * scale)
    nh = int(ph * scale)

    # HIGH QUALITY resize — LANCZOS = no blur, no distortion
    prod_r = product_img.resize((nw, nh), Image.LANCZOS)
    print(f"  Final size: {nw}x{nh} | Scale: {scale:.3f}")

    # Center horizontally — always centered regardless of angle
    x = (TARGET_W - nw) // 2

    # Vertical: center in upper 55-60% area, text stays below
    usable_h = int(TARGET_H * 0.57)
    y        = max(int(TARGET_H * 0.04), (usable_h - nh) // 2)

    # If product taller than usable area — push to very top
    if nh > usable_h:
        y = int(TARGET_H * 0.015)

    print(f"  Position: x={x}, y={y}")

    # Soft natural drop shadow
    shadow = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
    sd     = ImageDraw.Draw(shadow)
    sx     = x + nw // 2
    sy     = y + nh + 10
    sw     = int(nw * 0.58)
    for r in range(38, 0, -1):
        a = int(80 * (1 - r/38) ** 1.5)
        sd.ellipse([sx-sw//2-r, sy-r//5, sx+sw//2+r, sy+r//5], fill=(0, 0, 0, a))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))

    result = Image.alpha_composite(bg, shadow)
    result.paste(prod_r, (x, y), prod_r)
    print("  Composition complete!\n")
    return np.array(result.convert("RGB"))


# =============================================================================
#  VIDEO EFFECTS
# =============================================================================

def apply_shot(clip, shot, seg_dur):
    """Very gentle motion — product always fully visible, never cropped."""
    def shot_frame(get_frame, t):
        frame    = get_frame(t)
        fh, fw   = frame.shape[:2]
        progress = t / max(seg_dur, 0.001)
        ease     = progress * progress * (3 - 2 * progress)
        zoom     = shot["zoom_s"] + (shot["zoom_e"] - shot["zoom_s"]) * ease
        pan_x    = shot["px"]
        pan_y    = shot["py"] + 0.001 * np.sin(progress * np.pi)

        nw = max(1, int(fw / zoom))
        nh = max(1, int(fh / zoom))
        cx = int(fw/2 + pan_x * fw)
        cy = int(fh/2 + pan_y * fh)

        x1 = max(0, cx - nw//2); y1 = max(0, cy - nh//2)
        x2 = min(fw, x1 + nw);   y2 = min(fh, y1 + nh)
        if x2 > fw: x1 = fw - nw; x2 = fw
        if y2 > fh: y1 = fh - nh; y2 = fh
        x1 = max(0, x1); y1 = max(0, y1)

        cropped = frame[y1:y2, x1:x2]
        if cropped.size == 0:
            return frame
        return np.array(Image.fromarray(cropped).resize((fw, fh), Image.LANCZOS))
    return clip.fl(shot_frame)


def make_shimmer_frame(w, h, t, duration, color):
    img  = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    random.seed(42)
    for i in range(45):
        phase      = i / 45
        cycle      = (t / duration + phase) % 1.0
        brightness = np.sin(cycle * np.pi * 2) ** 2
        px   = int(w * (0.08 + 0.84 * random.random()))
        py   = int(h * (0.04 + 0.72 * random.random()))
        size = random.randint(2, 8)
        alpha= int(180 * brightness)
        if alpha > 15:
            cr = min(255, color[0]+50)
            cg = min(255, color[1]+40)
            cb = min(255, color[2]+45)
            draw.ellipse([px-size, py-size, px+size, py+size], fill=(cr, cg, cb, alpha))
            if size > 4:
                draw.line([px-size*2, py, px+size*2, py], fill=(255,220,225,alpha//2), width=1)
                draw.line([px, py-size*2, px, py+size*2], fill=(255,220,225,alpha//2), width=1)
    return np.array(img)


def make_shimmer_clip(w, h, duration, color):
    fps    = 24
    frames = int(duration * fps)
    imgs   = [make_shimmer_frame(w, h, i/fps, duration, color) for i in range(frames)]
    def mf(t): return imgs[min(int(t*fps), frames-1)][:,:,:3]
    def mm(t): return imgs[min(int(t*fps), frames-1)][:,:,3] / 255.0
    c      = VideoClip(mf, duration=duration)
    c.mask = VideoClip(mm, ismask=True, duration=duration)
    return c


def make_vignette_arr(w, h):
    ys, xs = np.mgrid[0:h, 0:w]
    cx, cy = w/2, h/2
    dx     = (xs - cx) / cx
    dy     = (ys - cy) / cy
    dist   = np.clip(np.sqrt(dx**2 + dy**2), 0, 1)
    alpha  = (190 * dist**2.2).astype(np.uint8)
    arr    = np.zeros((h, w, 4), dtype=np.uint8)
    arr[:,:,3] = alpha
    return np.array(Image.fromarray(arr, "RGBA").filter(ImageFilter.GaussianBlur(35)))


def get_font(size, bold=False):
    paths = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for fp in paths:
        try:
            return ImageFont.truetype(fp, size)
        except Exception:
            continue
    return ImageFont.load_default()


def text_arr(text, w, h, size, color, bold=False):
    img  = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = get_font(size, bold)
    try:
        bbox   = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    except Exception:
        tw, th = size * len(text)//2, size + 4
    x = max((w - tw)//2, 10)
    y = max((h - th)//2, 5)
    for dx, dy, a in [(4,4,180),(3,3,140),(2,2,100),(-1,-1,60)]:
        draw.text((x+dx, y+dy), text, font=font, fill=(0, 0, 0, a))
    draw.text((x, y), text, font=font, fill=(*color, 255))
    return np.array(img)


# =============================================================================
#  STEP 5 — Build Final Video
# =============================================================================

def build_video(base_arr, product_name, tagline, output_path):
    print("  Building professional video...")
    DURATION = 4.0
    seg_dur  = DURATION / len(SHOTS)
    color    = (220, 180, 200)

    vign_arr = make_vignette_arr(TARGET_W, TARGET_H)
    wm_a     = text_arr("* BeautyReel AI *", TARGET_W, 70,  28, (190, 145, 162))
    name_a   = text_arr(product_name,        TARGET_W, 160, 78, color, bold=True)
    tag_a    = text_arr(tagline,             TARGET_W, 85,  34, (252, 232, 238))

    line_img = Image.new("RGBA", (TARGET_W, 18), (0, 0, 0, 0))
    ld       = ImageDraw.Draw(line_img)
    lx       = (TARGET_W - 280)//2
    ld.rectangle([lx, 6, lx+280, 10], fill=(*color, 215))
    line_a   = np.array(line_img)

    shot_clips = []
    for i, shot in enumerate(SHOTS):
        print(f"       Shot {i+1}/{len(SHOTS)}: {shot['label']}")
        sdur      = seg_dur
        base_clip = ImageClip(base_arr).set_duration(sdur)
        base_clip = apply_shot(base_clip, shot, sdur)
        base_clip = colorx(base_clip, shot["bright"])

        shimmer = make_shimmer_clip(TARGET_W, TARGET_H, sdur, color)
        vign_c  = ImageClip(vign_arr).set_duration(sdur)

        bar_h   = 400
        bar_arr = np.zeros((bar_h, TARGET_W, 4), dtype=np.uint8)
        for row in range(bar_h):
            ratio = row / bar_h
            alpha = int(210 * np.sin(ratio * np.pi * 0.85))
            bar_arr[row, :] = [30, 15, 20, alpha]
        bar_c = ImageClip(bar_arr).set_duration(sdur).set_position((0, TARGET_H - bar_h))

        composed = CompositeVideoClip(
            [
                base_clip,
                shimmer, vign_c, bar_c,
                ImageClip(wm_a).set_duration(sdur).set_position(("center", 58)),
                ImageClip(name_a).set_duration(sdur).set_position(("center", TARGET_H-340)),
                ImageClip(line_a).set_duration(sdur).set_position(("center", TARGET_H-200)),
                ImageClip(tag_a).set_duration(sdur).set_position(("center", TARGET_H-160)),
            ],
            size=(TARGET_W, TARGET_H)
        )
        shot_clips.append(composed)

    final = concatenate_videoclips(shot_clips, method="compose")
    final = fadein(fadeout(final, 0.5), 0.5)
    final.write_videofile(
        str(output_path),
        fps=30, codec="libx264",
        bitrate="16000k",
        audio=False,
        threads=4, logger=None
    )


# =============================================================================
#  MAIN
# =============================================================================

def run():
    image_path, product_name, tagline, prompt, full_prompt = get_user_input()

    Path(OUTPUT_FOLDER).mkdir(parents=True, exist_ok=True)

    # Generate AI background
    bg_img = generate_background(full_prompt)
    if bg_img is None:
        print("ERROR: Background generation failed.")
        return

    safe_prompt = prompt[:25].lower().replace(" ","_").replace(",","").replace(".","")
    bg_save     = Path(OUTPUT_FOLDER) / f"bg_{safe_prompt}.png"
    bg_img.save(str(bg_save))
    print(f"  Background saved: {bg_save}")

    # Remove product background
    product_img = remove_product_bg(image_path)

    # Compose product on background
    composed_arr = compose_image(product_img, bg_img)

    # Build video
    safe_name   = product_name.lower().replace(" ", "_")
    output_path = Path(OUTPUT_FOLDER) / f"{safe_name}_{safe_prompt}_video.mp4"
    build_video(composed_arr, product_name, tagline, output_path)

    print("\n" + "="*60)
    print("  VIDEO READY!")
    print(f"  Product    : {product_name}")
    print(f"  Prompt     : {prompt}")
    print(f"  Background : {bg_save}")
    print(f"  Video      : {output_path}")
    print("  Add music in CapCut or Instagram!")
    print("="*60 + "\n")


if __name__ == "__main__":
    run()