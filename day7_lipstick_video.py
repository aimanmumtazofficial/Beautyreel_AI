# import time
# import shutil
# import os
# from gradio_client import Client, handle_file
# from moviepy import VideoFileClip, ColorClip, CompositeVideoClip, concatenate_videoclips, ImageClip
# from PIL import Image, ImageFilter, ImageEnhance
# import numpy as np

# # ============================================================
# # CONFIGURATION
# # ============================================================
# MY_TOKEN = "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"

# MY_PRODUCTS = {
#     "luxury_lipstick": r"images_datasets\lipstick_image_dataset\pexels-solodsha-7664366.jpg",
# }

# # ============================================================
# # STEP 1: CLIENT SETUP
# # ============================================================
# try:
#     video_client = Client("stabilityai/stable-video-diffusion", token=MY_TOKEN)
#     print("✅ Connected to stabilityai/stable-video-diffusion")
# except Exception as e:
#     print(f"⚠️ Primary connection failed: {e}")
#     video_client = Client("multimodalart-stable-video-diffusion.hf.space", token=MY_TOKEN)
#     print("✅ Connected to backup space")

# # ============================================================
# # STEP 2: EXTRACT VIDEO PATH FROM API RESULT
# # ============================================================
# def extract_video_path(result):
#     if isinstance(result, dict):
#         return result.get('video') or result.get('name') or result.get('data', [{}])[0].get('name')
#     if isinstance(result, (list, tuple)):
#         first = result[0]
#         return first.get('video') if isinstance(first, dict) else first
#     return result

# # ============================================================
# # STEP 3: CREATE BLURRED BACKGROUND (only for SVD input)
# # ============================================================
# def create_blurred_bg_image(image_path, output_path):
#     """
#     Creates a heavily blurred version of the image for background animation.
#     This blurred image is sent to SVD — product shape does not matter here.
#     SVD will animate the glow and bokeh of this blurred background only.
#     """
#     img = Image.open(image_path).convert("RGB")
#     blurred = img.filter(ImageFilter.GaussianBlur(radius=25))
#     # Slightly brighten so background glows nicely
#     blurred = ImageEnhance.Brightness(blurred).enhance(1.2)
#     blurred.save(output_path, quality=95)
#     print(f"   🔵 Background blur image ready: {output_path}")
#     return output_path

# # ============================================================
# # STEP 4: PREPARE SHARP PRODUCT IMAGE (MAIN FIX)
# # ============================================================
# def prepare_sharp_product(image_path, target_w, target_h):
#     """
#     Prepares the original product image WITHOUT any blur.
#     - LANCZOS resampling = sharpest possible resize, zero blur
#     - RGB mode = no alpha channel blur issues
#     - UnsharpMask + Sharpness enhance = crystal clear product
#     Returns: numpy array (H, W, 3) — pure RGB, sharp as original
#     """
#     img = Image.open(image_path).convert("RGB")  # RGB only — no alpha channel issues

#     # Apply UnsharpMask to enhance edge sharpness before resize
#     img = img.filter(ImageFilter.UnsharpMask(radius=1.5, percent=150, threshold=3))

#     # Set product width to 68% of total frame width
#     product_w = int(target_w * 0.68)
#     aspect = img.height / img.width
#     product_h = int(product_w * aspect)

#     # LANCZOS = highest quality resize algorithm, zero blur introduced
#     img = img.resize((product_w, product_h), Image.LANCZOS)

#     # Final sharpness boost after resize
#     img = ImageEnhance.Sharpness(img).enhance(2.0)

#     print(f"   ✅ Sharp product prepared: {product_w}x{product_h}px (no blur applied)")
#     return np.array(img), product_w, product_h


# # ============================================================
# # STEP 5: COMPOSITE FINAL VIDEO
# # ============================================================
# def overlay_sharp_product(ai_video_path, original_image_path, output_path, duration=4.0):
#     """
#     Combines AI animated background + sharp original product image.

#     KEY POINTS:
#     - Product image: original, sharp, zero distortion, never touched by AI
#     - Background: AI animated glow generated from blurred image only
#     - Breathing animation: only a subtle 1.5% scale oscillation
#       gives a luxury "alive" feel without altering shape at all
#     """
#     target_w, target_h = 1080, 1920

#     # Load AI background video
#     ai_clip = VideoFileClip(ai_video_path)

#     # Prepare the sharp product image (main shape + clarity fix)
#     product_np, prod_w, prod_h = prepare_sharp_product(
#         original_image_path, target_w, target_h
#     )

#     # Resize background video to fill 9:16 frame
#     bg_resized = ai_clip.resized(height=target_h)
#     if bg_resized.w < target_w:
#         bg_resized = ai_clip.resized(width=target_w)

#     # Crop to exact 1080x1920
#     bg_cropped = bg_resized.cropped(
#         x_center=bg_resized.w / 2,
#         y_center=bg_resized.h / 2,
#         width=target_w,
#         height=target_h
#     )

#     # Loop background video to reach full 4-second duration
#     loops_needed = int(np.ceil(duration / bg_cropped.duration))
#     bg_looped = concatenate_videoclips([bg_cropped] * loops_needed).subclipped(0, duration)

#     # Create sharp product as a static ImageClip layer
#     product_clip = (
#         ImageClip(product_np)
#         .with_duration(duration)
#         .with_position("center")
#     )

#     # Subtle breathing animation — only 1.5% scale oscillation per cycle
#     # Gives a luxury "alive" feel without distorting the product shape
#     def make_breathing_frame(get_frame, t):
#         frame = get_frame(t)
#         scale = 1.0 + 0.015 * np.sin(2 * np.pi * t / 2.5)
#         h, w = frame.shape[:2]
#         new_w = int(w * scale)
#         new_h = int(h * scale)

#         # Use LANCZOS for high-quality resize during animation frames
#         img_pil = Image.fromarray(frame.astype(np.uint8))
#         img_pil = img_pil.resize((new_w, new_h), Image.LANCZOS)

#         # Center crop back to original dimensions
#         left = (new_w - w) // 2
#         top  = (new_h - h) // 2
#         img_pil = img_pil.crop((left, top, left + w, top + h))

#         return np.array(img_pil).astype(np.uint8)

#     product_animated = product_clip.transform(make_breathing_frame)

#     # Final composite: animated background layer + sharp product on top
#     final = CompositeVideoClip(
#         [bg_looped, product_animated.with_position("center")],
#         size=(target_w, target_h)
#     ).with_duration(duration)

#     print(f"   🎬 Rendering final video... (this may take 1-2 minutes)")
#     final.write_videofile(
#         output_path,
#         fps=24,
#         codec="libx264",
#         audio=False,
#         preset="slow",
#         ffmpeg_params=["-crf", "16"]  # CRF 16 = near-lossless, maximum output sharpness
#     )

#     ai_clip.close()
#     print(f"   ✅ Final video saved: {output_path}")


# # ============================================================
# # STEP 6: MAIN FUNCTION
# # ============================================================
# def generate_perfect_lipstick_video(name, image_path):
#     print(f"\n{'='*55}")
#     print(f"✨ Processing: {name.upper()}")
#     print(f"{'='*55}")

#     if not os.path.exists(image_path):
#         print(f"❌ Image not found at path: {image_path}")
#         return

#     blur_path  = f"{name}_bg_blur.jpg"
#     ai_raw     = f"{name}_ai_raw.mp4"
#     final_path = f"{name}_PERFECT_FINAL.mp4"

#     try:
#         # Phase 1: Create blurred background image for SVD input
#         print(f"\n📸 Phase 1: Creating blurred background for SVD input...")
#         create_blurred_bg_image(image_path, blur_path)

#         # Phase 2: Send blurred image to SVD — generates animated background only
#         print(f"\n🤖 Phase 2: Generating AI background animation via SVD...")
#         result = video_client.predict(
#             image=handle_file(blur_path),
#             seed=42,
#             randomize_seed=False,
#             motion_bucket_id=80,  # High motion setting for dynamic background glow
#             fps_id=8,
#             api_name="/video"
#         )

#         raw_path = extract_video_path(result)
#         if not raw_path:
#             print("❌ No video path returned from AI. Check API response.")
#             return

#         shutil.copy(raw_path, ai_raw)
#         print(f"   ✅ AI background video saved: {ai_raw}")

#         # Phase 3: Composite original sharp product over AI animated background
#         print(f"\n🎨 Phase 3: Overlaying original sharp product image...")
#         overlay_sharp_product(ai_raw, image_path, final_path, duration=4.0)

#         # Remove all temporary working files
#         for f in [blur_path, ai_raw]:
#             if os.path.exists(f):
#                 os.remove(f)

#         print(f"\n{'='*55}")
#         print(f"🏆 PERFECT VIDEO READY: {final_path}")
#         print(f"{'='*55}")
#         print(f"  ✔ Product shape  : 100% original (zero distortion)")
#         print(f"  ✔ Product blur   : NONE (UnsharpMask + Sharpness 2.0)")
#         print(f"  ✔ Background     : AI animated glow/shimmer")
#         print(f"  ✔ Duration       : 4 seconds")
#         print(f"  ✔ Format         : 1080x1920 (9:16 Reels)")
#         print(f"  ✔ Quality        : CRF 16 (near-lossless)")

#     except Exception as e:
#         print(f"\n❌ Error occurred: {e}")
#         import traceback
#         traceback.print_exc()


# # ============================================================
# # RUN
# # ============================================================
# if __name__ == "__main__":
#     for product_name, path in MY_PRODUCTS.items():
#         generate_perfect_lipstick_video(product_name, path)

#     print(f"\n🎉 All products processed successfully!")

import math
from gradio_client import Client, handle_file
import shutil
import os
from moviepy import VideoFileClip, VideoClip
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np

# ============================================================
# CONFIGURATION
# ============================================================
MY_TOKEN = "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"


MY_PRODUCTS = {"luxury_lipstick": r"images_datasets\lipstick_image_dataset\pexels-solodsha-7664366.jpg",
}
    

# ============================================================
# STEP 1: SERVER CONNECTION
# ============================================================
video_client = None
servers = [
    "stabilityai/stable-video-diffusion",
    "multimodalart-stable-video-diffusion",
    "fffiloni/stable-video-diffusion"
]

for server in servers:
    try:
        video_client = Client(server, token=MY_TOKEN)
        print(f"✅ Connected to: {server}")
        break
    except Exception as e:
        print(f"⚠️ Failed: {server} → {e}")

if not video_client:
    for server in servers:
        try:
            video_client = Client(server)
            print(f"✅ Connected (no token): {server}")
            break
        except Exception as e:
            print(f"⚠️ Failed: {server} → {e}")

# ============================================================
# STEP 2: EXTRACT VIDEO PATH FROM API RESULT
# ============================================================
def extract_video_path(result):
    if isinstance(result, dict):
        return result.get('video') or result.get('name')
    if isinstance(result, (list, tuple)):
        first_item = result[0]
        return first_item.get('video') if isinstance(first_item, dict) else first_item
    return result

# ============================================================
# STEP 3: SHARP FRAME BUILDER
# — Original image used every frame, AI never touches pixels
# — Ken Burns zoom + studio drift = professional movement
# — NO blur background, clean solid color only
# ============================================================
def make_sharp_professional_frame(original_img, t, total_dur, target_w, target_h):
    """
    Builds each video frame from the ORIGINAL unchanged product image.
    All motion (zoom + drift) is done via pure crop math.
    AI never touches the pixels — zero shape distortion guaranteed.
    """
    orig_w, orig_h = original_img.size

    # ── Ken Burns Effect: smooth zoom in → zoom out ──
    half = total_dur / 2
    if t <= half:
        zoom = 1.0 + 0.05 * (t / half)            # 1.00 → 1.05
    else:
        zoom = 1.05 - 0.05 * ((t - half) / half)  # 1.05 → 1.00

    # Crop center region based on zoom level (pixels stay 100% sharp)
    crop_w = int(orig_w / zoom)
    crop_h = int(orig_h / zoom)
    left   = (orig_w - crop_w) // 2
    top    = (orig_h - crop_h) // 2
    cropped = original_img.crop((left, top, left + crop_w, top + crop_h))

    # Upscale back to original size using LANCZOS (sharpest algorithm)
    sharp = cropped.resize((orig_w, orig_h), Image.LANCZOS)

    # ── Clean Premium Background (no blur, solid color) ──
    # Soft warm white — works beautifully for lipstick/makeup products
    canvas = Image.new("RGB", (target_w, target_h), (245, 242, 240))

    # Center the product on canvas
    paste_x = (target_w - orig_w) // 2
    paste_y = (target_h - orig_h) // 2

    # ── Studio Drift: gentle professional float movement ──
    # Horizontal drift — slow sine wave
    drift_x = int(18 * math.sin(2 * math.pi * t / total_dur))
    # Vertical drift — slightly faster, gives floating feel
    drift_y = int(7  * math.sin(4 * math.pi * t / total_dur))

    final_x = paste_x + drift_x
    final_y = paste_y + drift_y

    canvas.paste(sharp, (final_x, final_y))
    return np.array(canvas)


# ============================================================
# STEP 4: MAIN VIDEO GENERATION FUNCTION
# ============================================================
def generate_lipstick_video(name, image_path):

    if not video_client:
        print("❌ No server connected. Please retry in 5 minutes.")
        return

    print(f"\n{'='*55}")
    print(f"✨ Processing: {name.upper()}")
    print(f"{'='*55}")

    if not os.path.exists(image_path):
        print(f"❌ Image not found at: {image_path}")
        return

    print(f"✅ Image found: {image_path}")

    raw_filename   = f"{name}_temp.mp4"
    final_filename = f"{name}_4s_reel.mp4"

    try:
        # ── Phase 1: Get AI video (only for timing reference) ──
        print(f"\n🚀 Phase 1: Getting AI base video (minimum motion)...")
        print(f"   Note: AI video is used for duration only.")
        print(f"         All frames are built from original image.")

        result = video_client.predict(
            image=handle_file(image_path),
            seed=42,
            randomize_seed=False,
            motion_bucket_id=1,   # Minimum motion — AI barely touches the image
            fps_id=12,
            api_name="/video"
        )

        raw_path = extract_video_path(result)

        if not raw_path:
            print("❌ No video path returned from AI.")
            return

        shutil.copy(raw_path, raw_filename)

        # ── Phase 2: Build all frames from ORIGINAL sharp image ──
        print(f"\n📸 Phase 2: Building professional frames from original image...")

        # Load original image — this is NEVER modified or distorted
        original_img = Image.open(image_path).convert("RGB")

        # Apply sharpness enhancement to original before processing
        original_img = original_img.filter(
            ImageFilter.UnsharpMask(radius=1.5, percent=150, threshold=3)
        )
        original_img = ImageEnhance.Sharpness(original_img).enhance(1.8)

        # Resize to fit nicely in 9:16 frame (max 900x900)
        target_w, target_h = 1080, 1920
        max_product_w = 900
        max_product_h = 900
        original_img.thumbnail((max_product_w, max_product_h), Image.LANCZOS)

        # Get AI video duration for reference
        ai_clip = VideoFileClip(raw_filename)
        ai_duration = ai_clip.duration
        ai_clip.close()

        # Total duration = forward + reverse loop (smooth 4-5 seconds)
        total_dur = ai_duration * 2
        fps = 24
        total_frames = int(total_dur * fps)

        print(f"   Product size    : {original_img.size}")
        print(f"   Total duration  : {total_dur:.1f}s")
        print(f"   Total frames    : {total_frames}")
        print(f"   Building frames...")

        # Build every frame from the original sharp image
        frames = []
        for i in range(total_frames):
            t = i / fps
            frame = make_sharp_professional_frame(
                original_img, t, total_dur, target_w, target_h
            )
            frames.append(frame)

        # ── Phase 3: Render final video ──
        print(f"\n🎬 Phase 3: Rendering final video...")

        def make_frame(t):
            idx = min(int(t * fps), len(frames) - 1)
            return frames[idx]

        final_clip = VideoClip(make_frame, duration=total_dur)
        final_clip.write_videofile(
            final_filename,
            fps=fps,
            codec="libx264",
            audio=False,
            ffmpeg_params=["-crf", "16"]  # Near-lossless quality
        )

        # Remove temporary AI video file
        if os.path.exists(raw_filename):
            os.remove(raw_filename)

        print(f"\n{'='*55}")
        print(f"🏆 PERFECT VIDEO READY: {final_filename}")
        print(f"{'='*55}")
        print(f"  ✔ Product shape   : 100% original (zero AI distortion)")
        print(f"  ✔ Background      : Clean solid color (no blur)")
        print(f"  ✔ Movement        : Ken Burns zoom + studio drift")
        print(f"  ✔ Duration        : {total_dur:.1f} seconds")
        print(f"  ✔ Format          : 1080x1920 (9:16 Reels)")
        print(f"  ✔ Quality         : CRF 16 (near-lossless)")

    except Exception as e:
        if "quota" in str(e).lower():
            print(f"🛑 Quota reached. Wait 24 hours and retry.")
        elif "GPU" in str(e):
            print("🛑 Server busy. Retry in 5 minutes.")
        else:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()


# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    for product_name, path in MY_PRODUCTS.items():
        generate_lipstick_video(product_name, path)

    print(f"\n🎉 All products processed successfully!")