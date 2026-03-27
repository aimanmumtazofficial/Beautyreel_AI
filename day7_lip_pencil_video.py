# import time
# from gradio_client import Client, handle_file
# import shutil
# import os
# from moviepy import VideoFileClip, ColorClip, CompositeVideoClip, concatenate_videoclips

# # --- 1. SETUP & AUTHENTICATION ---
# MY_TOKEN = "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"

# # ✅ Lip Pencil Image Path
# MY_PRODUCTS = {
#     "flawless_lip_pencil": r"images_datasets\lip_pencil_image_dataset\download (1).jpg",
# }

# # ✅ Server Connection (Token without hf_token keyword)
# try:
#     video_client = Client("stabilityai/stable-video-diffusion", token=MY_TOKEN)
#     print("✅ Connected to: stabilityai/stable-video-diffusion")
# except Exception as e:
#     print(f"⚠️ Primary server failed: {e}")
#     try:
#         video_client = Client("multimodalart-stable-video-diffusion", token=MY_TOKEN)
#         print("✅ Connected to: multimodalart-stable-video-diffusion")
#     except Exception as e2:
#         print(f"⚠️ Backup server failed: {e2}")
#         try:
#             video_client = Client("fffiloni/stable-video-diffusion", token=MY_TOKEN)
#             print("✅ Connected to: fffiloni/stable-video-diffusion")
#         except Exception as e3:
#             print(f"❌ All servers failed: {e3}")
#             video_client = None

# # --- 2. SAFE PATH EXTRACTION ---
# def extract_video_path(result):
#     if isinstance(result, dict):
#         return result.get('video') or result.get('name')
#     if isinstance(result, (list, tuple)):
#         first_item = result[0]
#         return first_item.get('video') if isinstance(first_item, dict) else first_item
#     return result

# # --- 3. LIP PENCIL VIDEO GENERATION FUNCTION ---
# def generate_stable_video(name, image_path):

#     if not video_client:
#         print("❌ No server connected. Please retry.")
#         return

#     print(f"\n✨ Starting 4-5 Second Video for: {name.upper()}")

#     if not os.path.exists(image_path):
#         print(f"❌ Error: File NOT found at: {image_path}")
#         return

#     print(f"✅ Image found: {image_path}")

#     try:
#         print(f"🚀 Step 1: Generating AI Motion...")

#         result = video_client.predict(
#             image=handle_file(image_path),
#             seed=42,
#             randomize_seed=False,
#             motion_bucket_id=1,   # ✅ Minimum motion — pencil shape preserved, no forward/backward movement
#             fps_id=12,
#             api_name="/video"
#         )

#         raw_path = extract_video_path(result)

#         if raw_path:
#             raw_filename = f"{name}_temp.mp4"
#             final_filename = f"{name}_4s_reel.mp4"
#             shutil.copy(raw_path, raw_filename)

#             # --- PHASE 2: STRETCH TO 4+ SECONDS & FORMAT 9:16 ---
#             try:
#                 print(f"📏 Step 2: Stretching duration and formatting to 9:16...")

#                 # Load the 2-second clip
#                 clip = VideoFileClip(raw_filename)

#                 # ✅ Reverse clip for seamless mirror loop
#                 reversed_clip = clip.transform(lambda get_frame, t: get_frame(clip.duration - t))

#                 # ✅ Forward + Backward = 4 to 5 seconds total
#                 long_clip = concatenate_videoclips([clip, reversed_clip])

#                 # ✅ Gentle 3% Ken Burns zoom — pencil stays centered, no shape distortion
#                 zoomed_clip = long_clip.resized(lambda t: 1 + 0.03 * (t / long_clip.duration))

#                 # ✅ 9:16 Vertical Format (Instagram/TikTok ready)
#                 target_w, target_h = 1080, 1920

#                 # ✅ White background — premium look for lip pencil
#                 background = ColorClip(
#                     size=(target_w, target_h),
#                     color=(255, 255, 255)
#                 ).with_duration(long_clip.duration)

#                 # ✅ Lip pencil perfectly centered — cap & pencil stay in place
#                 final = CompositeVideoClip([
#                     background,
#                     zoomed_clip.with_position("center")
#                 ])

#                 print(f"🎬 Step 3: Rendering final file...")
#                 final.write_videofile(
#                     final_filename,
#                     fps=24,
#                     codec="libx264",
#                     audio=False
#                 )

#                 # Cleanup temp file
#                 clip.close()
#                 if os.path.exists(raw_filename):
#                     os.remove(raw_filename)

#                 print(f"\n✅ SUCCESS! Your 4-second lip pencil video is ready: {final_filename}")
#                 print(f"   📌 Shape preserved | Cap in place | No forward/backward movement")

#             except Exception as e:
#                 print(f"⚠️ Video processing failed: {e}")

#     except Exception as e:
#         if "quota" in str(e).lower():
#             print(f"🛑 Error: Quota reached. Wait for 24h reset.")
#         elif "GPU" in str(e):
#             print("🛑 Server Busy: Retry in 5 minutes.")
#         else:
#             print(f"❌ AI Error: {e}")

# # --- 4. EXECUTION ---
# if __name__ == "__main__":
#     for product_name, path in MY_PRODUCTS.items():
#         generate_stable_video(product_name, path)


import math
from gradio_client import Client, handle_file
import shutil
import os
from moviepy import VideoFileClip, ColorClip, CompositeVideoClip, concatenate_videoclips
from PIL import Image
import numpy as np

# --- 1. SETUP & AUTHENTICATION ---
MY_TOKEN = "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"

# ✅ Lip Pencil Image Path
MY_PRODUCTS = {
    "flawless_lip_pencil": r"images_datasets\lip_pencil_image_dataset\download (1).jpg",
}

# ✅ Server Connection
try:
    video_client = Client("stabilityai/stable-video-diffusion", token=MY_TOKEN)
    print("✅ Connected to: stabilityai/stable-video-diffusion")
except Exception as e:
    print(f"⚠️ Primary server failed: {e}")
    try:
        video_client = Client("multimodalart-stable-video-diffusion", token=MY_TOKEN)
        print("✅ Connected to: multimodalart-stable-video-diffusion")
    except Exception as e2:
        print(f"⚠️ Backup 1 failed: {e2}")
        try:
            video_client = Client("fffiloni/stable-video-diffusion", token=MY_TOKEN)
            print("✅ Connected to: fffiloni/stable-video-diffusion")
        except Exception as e3:
            print(f"❌ All servers failed: {e3}")
            video_client = None

# --- 2. SAFE PATH EXTRACTION ---
def extract_video_path(result):
    if isinstance(result, dict):
        return result.get('video') or result.get('name')
    if isinstance(result, (list, tuple)):
        first_item = result[0]
        return first_item.get('video') if isinstance(first_item, dict) else first_item
    return result

# ✅ SHARP ZOOM — No Blur Fix
# Instead of resizing the video (which causes blur),
# we crop into a larger canvas so pixels stay sharp
def make_sharp_zoom_frame(get_frame, t, total_dur, target_w, target_h):
    frame = get_frame(t)  # Get original sharp frame
    img = Image.fromarray(frame)
    orig_w, orig_h = img.size

    # Zoom factor: 1.0 → 1.08 → 1.0 (Ken Burns)
    half = total_dur / 2
    if t <= half:
        zoom = 1.0 + 0.08 * (t / half)
    else:
        zoom = 1.08 - 0.08 * ((t - half) / half)

    # ✅ CROP instead of RESIZE — keeps pixels sharp
    crop_w = int(orig_w / zoom)
    crop_h = int(orig_h / zoom)
    left   = (orig_w - crop_w) // 2
    top    = (orig_h - crop_h) // 2
    cropped = img.crop((left, top, left + crop_w, top + crop_h))

    # ✅ LANCZOS resampling — highest quality, sharpest upscale
    sharp = cropped.resize((orig_w, orig_h), Image.LANCZOS)

    # ✅ Place on white 9:16 canvas, centered
    canvas = Image.new("RGB", (target_w, target_h), (255, 255, 255))
    paste_x = (target_w - orig_w) // 2

    # Studio drift: subtle sine wave movement
    drift_x = int(30 * math.sin(2 * math.pi * t / total_dur))
    drift_y = int(10 * math.sin(4 * math.pi * t / total_dur))
    paste_y = (target_h - orig_h) // 2

    canvas.paste(sharp, (paste_x + drift_x, paste_y + drift_y))
    return np.array(canvas)


# --- 3. PROFESSIONAL LIP PENCIL VIDEO FUNCTION ---
def generate_stable_video(name, image_path):

    if not video_client:
        print("❌ No server connected. Please retry.")
        return

    print(f"\n✨ Starting Professional Product Video for: {name.upper()}")

    if not os.path.exists(image_path):
        print(f"❌ Error: File NOT found at: {image_path}")
        return

    print(f"✅ Image found: {image_path}")

    try:
        print(f"🚀 Step 1: Generating AI Motion...")

        result = video_client.predict(
            image=handle_file(image_path),
            seed=42,
            randomize_seed=False,
            motion_bucket_id=25,  # ✅ Professional subtle motion
            fps_id=12,
            api_name="/video"
        )

        raw_path = extract_video_path(result)

        if raw_path:
            raw_filename = f"{name}_temp.mp4"
            final_filename = f"{name}_4s_reel.mp4"
            shutil.copy(raw_path, raw_filename)

            try:
                print(f"📏 Step 2: Applying sharp professional effects...")

                clip = VideoFileClip(raw_filename)

                # ✅ Seamless mirror loop
                reversed_clip = clip.transform(
                    lambda get_frame, t: get_frame(clip.duration - t)
                )
                long_clip = concatenate_videoclips([clip, reversed_clip])
                total_dur = long_clip.duration

                target_w, target_h = 1080, 1920

                # ✅ Apply sharp zoom + drift using crop method (NO blur)
                final_clip = long_clip.transform(
                    lambda get_frame, t: make_sharp_zoom_frame(
                        get_frame, t, total_dur, target_w, target_h
                    ),
                    apply_to="video"
                )
                final_clip = final_clip.with_effects([])  # reset size metadata

                # ✅ Force correct output size
                from moviepy import vfx
                final_clip = final_clip.resized((target_w, target_h))

                print(f"🎬 Step 3: Rendering sharp professional video...")
                final_clip.write_videofile(
                    final_filename,
                    fps=24,
                    codec="libx264",
                    audio=False,
                    ffmpeg_params=["-crf", "18"]  # ✅ High quality encoding, less compression
                )

                clip.close()
                if os.path.exists(raw_filename):
                    os.remove(raw_filename)

                print(f"\n✅ SUCCESS! Sharp professional video ready: {final_filename}")
                print(f"   📌 NO blur | Ken Burns crop zoom | Studio drift | Shape preserved")

            except Exception as e:
                print(f"⚠️ Video processing failed: {e}")

    except Exception as e:
        if "quota" in str(e).lower():
            print(f"🛑 Quota reached. Wait 24h and retry.")
        elif "GPU" in str(e):
            print("🛑 Server Busy: Retry in 5 minutes.")
        else:
            print(f"❌ AI Error: {e}")

# --- 4. EXECUTION ---
if __name__ == "__main__":
    for product_name, path in MY_PRODUCTS.items():
        generate_stable_video(product_name, path)