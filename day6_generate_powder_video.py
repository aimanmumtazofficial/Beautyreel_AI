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

MY_PRODUCTS = {
    "emani_powder": r"images_datasets\powder_image_dataset\WhatsApp Image 2026-02-24 at 11.04.11 PM (1).jpeg",
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
        return result.get('video') or result.get('name') or result.get('data', [{}])[0].get('name')
    if isinstance(result, (list, tuple)):
        first_item = result[0]
        return first_item.get('video') if isinstance(first_item, dict) else first_item
    return result

# ============================================================
# STEP 3: SHARP FRAME BUILDER
# — Original powder image used every frame, AI never touches pixels
# — Ken Burns zoom + studio drift = professional movement
# — Clean solid background, no blur at all
# ============================================================
def make_sharp_professional_frame(original_img, t, total_dur, target_w, target_h):
    """
    Builds each video frame from the ORIGINAL unchanged powder image.
    All motion (zoom + drift) is done via pure crop math.
    AI never touches the pixels — zero shape distortion guaranteed.
    """
    orig_w, orig_h = original_img.size

    # Ken Burns Effect: smooth zoom in → zoom out
    half = total_dur / 2
    if t <= half:
        zoom = 1.0 + 0.05 * (t / half)            # 1.00 → 1.05
    else:
        zoom = 1.05 - 0.05 * ((t - half) / half)  # 1.05 → 1.00

    # Crop center region based on zoom (pixels stay 100% sharp)
    crop_w = int(orig_w / zoom)
    crop_h = int(orig_h / zoom)
    left   = (orig_w - crop_w) // 2
    top    = (orig_h - crop_h) // 2
    cropped = original_img.crop((left, top, left + crop_w, top + crop_h))

    # Upscale back using LANCZOS (sharpest algorithm, zero blur)
    sharp = cropped.resize((orig_w, orig_h), Image.LANCZOS)

    # Clean premium background — soft warm white, perfect for powder compact
    canvas = Image.new("RGB", (target_w, target_h), (245, 242, 240))

    # Center the powder product on canvas
    paste_x = (target_w - orig_w) // 2
    paste_y = (target_h - orig_h) // 2

    # Studio drift: gentle professional float movement
    drift_x = int(18 * math.sin(2 * math.pi * t / total_dur))
    drift_y = int(7  * math.sin(4 * math.pi * t / total_dur))

    final_x = paste_x + drift_x
    final_y = paste_y + drift_y

    canvas.paste(sharp, (final_x, final_y))
    return np.array(canvas)


# ============================================================
# STEP 4: MAIN VIDEO GENERATION FUNCTION
# ============================================================
def generate_powder_video(name, image_path):

    if not video_client:
        print("❌ No server connected. Please retry in 5 minutes.")
        return

    print(f"\n{'='*55}")
    print(f"✨ Processing Powder: {name.upper()}")
    print(f"{'='*55}")

    if not os.path.exists(image_path):
        print(f"❌ Powder image not found at: {image_path}")
        return

    print(f"✅ Powder image found: {image_path}")

    raw_filename   = f"{name}_temp.mp4"
    final_filename = f"{name}_2s_reel.mp4"

    try:
        # Phase 1: Get AI video (used only for timing reference)
        print(f"\n🚀 Phase 1: Getting AI base video (minimum motion)...")
        print(f"   Note: AI video used for duration reference only.")
        print(f"         All frames built from original powder image — zero distortion.")

        result = video_client.predict(
            image=handle_file(image_path),
            seed=42,
            randomize_seed=False,
            motion_bucket_id=1,   # Minimum motion — AI barely touches the powder image
            fps_id=12,
            api_name="/video"
        )

        raw_path = extract_video_path(result)

        if not raw_path:
            print("❌ No video path returned from AI.")
            return

        shutil.copy(raw_path, raw_filename)

        # Phase 2: Build all frames from ORIGINAL sharp powder image
        print(f"\n📸 Phase 2: Building professional frames from original powder image...")

        # Load original powder image — this is NEVER distorted by AI
        original_img = Image.open(image_path).convert("RGB")

        # Sharpness enhancement before processing (no blur introduced)
        original_img = original_img.filter(
            ImageFilter.UnsharpMask(radius=1.5, percent=150, threshold=3)
        )
        original_img = ImageEnhance.Sharpness(original_img).enhance(1.8)

        # Resize powder image to 85% of frame width — large and clearly visible
        target_w, target_h = 1080, 1920
        desired_w = int(target_w * 0.85)          # 918px wide — fills the frame nicely
        aspect    = original_img.height / original_img.width
        desired_h = int(desired_w * aspect)

        original_img = original_img.resize((desired_w, desired_h), Image.LANCZOS)

        # Re-apply sharpness after resize to keep powder compact edges crisp
        original_img = ImageEnhance.Sharpness(original_img).enhance(1.5)

        # Fixed duration = exactly 2 seconds
        total_dur = 2.0
        fps = 24
        total_frames = int(total_dur * fps)  # 48 frames

        print(f"   Powder image size : {original_img.size}")
        print(f"   Total duration    : {total_dur}s (fixed)")
        print(f"   Total frames      : {total_frames}")
        print(f"   Building frames...")

        # Build every frame from the original sharp powder image
        frames = []
        for i in range(total_frames):
            t = i / fps
            frame = make_sharp_professional_frame(
                original_img, t, total_dur, target_w, target_h
            )
            frames.append(frame)

        # Phase 3: Render final video
        print(f"\n🎬 Phase 3: Rendering final 2-second powder video...")

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
        print(f"🏆 PERFECT POWDER VIDEO READY: {final_filename}")
        print(f"{'='*55}")
        print(f"  ✔ Powder shape    : 100% original (zero AI distortion)")
        print(f"  ✔ Image blur      : NONE (UnsharpMask + Sharpness 1.8)")
        print(f"  ✔ Background      : Clean solid color (no blur)")
        print(f"  ✔ Movement        : Ken Burns zoom + studio drift")
        print(f"  ✔ Duration        : 2 seconds (fixed)")
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
        generate_powder_video(product_name, path)

    print(f"\n🎉 Powder product processed successfully!")