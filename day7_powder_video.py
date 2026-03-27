# import math
# from gradio_client import Client, handle_file
# import shutil
# import os
# from moviepy import VideoFileClip, ColorClip, CompositeVideoClip, concatenate_videoclips
# from PIL import Image
# import numpy as np

# # --- 1. SETUP & AUTHENTICATION ---
# MY_TOKEN = "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"

# # ✅ Powder Image Path
# MY_PRODUCTS = {
#     "emani_powder": r"images_datasets\powder_image_dataset\WhatsApp Image 2026-02-24 at 11.04.11 PM (1).jpeg",
# }

# # ✅ Server Connection (3 fallback servers)
# video_client = None
# servers = [
#     "stabilityai/stable-video-diffusion",
#     "multimodalart-stable-video-diffusion",
#     "fffiloni/stable-video-diffusion"
# ]

# for server in servers:
#     try:
#         video_client = Client(server, token=MY_TOKEN)
#         print(f"✅ Connected to: {server}")
#         break
#     except Exception as e:
#         print(f"⚠️ Failed: {server} → {e}")

# if not video_client:
#     # Retry without token
#     for server in servers:
#         try:
#             video_client = Client(server)
#             print(f"✅ Connected (no token): {server}")
#             break
#         except Exception as e:
#             print(f"⚠️ Failed: {server} → {e}")

# # --- 2. SAFE PATH EXTRACTION ---
# def extract_video_path(result):
#     if isinstance(result, dict):
#         return result.get('video') or result.get('name')
#     if isinstance(result, (list, tuple)):
#         first_item = result[0]
#         return first_item.get('video') if isinstance(first_item, dict) else first_item
#     return result

# # ✅ SHARP ZOOM — CROP method (NO blur, sponge & powder stay intact)
# # Crop into frame instead of stretching pixels = always sharp
# def make_sharp_zoom_frame(get_frame, t, total_dur, target_w, target_h):
#     frame = get_frame(t)
#     img = Image.fromarray(frame)
#     orig_w, orig_h = img.size

#     # ✅ Ken Burns: zoom in first half, zoom out second half
#     half = total_dur / 2
#     if t <= half:
#         zoom = 1.0 + 0.06 * (t / half)          # 1.0 → 1.06 (gentle for round product)
#     else:
#         zoom = 1.06 - 0.06 * ((t - half) / half) # 1.06 → 1.0

#     # ✅ CROP center instead of resize (keeps pixels sharp)
#     crop_w = int(orig_w / zoom)
#     crop_h = int(orig_h / zoom)
#     left   = (orig_w - crop_w) // 2
#     top    = (orig_h - crop_h) // 2
#     cropped = img.crop((left, top, left + crop_w, top + crop_h))

#     # ✅ LANCZOS — sharpest resampling algorithm
#     sharp = cropped.resize((orig_w, orig_h), Image.LANCZOS)

#     # ✅ Soft gray background — premium for powder/compact products
#     canvas = Image.new("RGB", (target_w, target_h), (240, 240, 242))

#     # Center position
#     paste_x = (target_w - orig_w) // 2
#     paste_y = (target_h - orig_h) // 2

#     # ✅ Studio drift — very gentle rotation feel (powder is round, subtle is better)
#     # Small circular drift: product rotates slightly in place
#     drift_x = int(20 * math.sin(2 * math.pi * t / total_dur))   # ±20px horizontal
#     drift_y = int(8  * math.sin(4 * math.pi * t / total_dur))   # ±8px vertical

#     canvas.paste(sharp, (paste_x + drift_x, paste_y + drift_y))
#     return np.array(canvas)


# # --- 3. PROFESSIONAL POWDER VIDEO FUNCTION ---
# def generate_stable_video(name, image_path):

#     if not video_client:
#         print("❌ No server connected. Please retry in 5 minutes.")
#         return

#     print(f"\n✨ Starting Professional Product Video for: {name.upper()}")

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
#             motion_bucket_id=20,  # ✅ Subtle professional motion for compact powder
#                                    #    Sponge & lid stay in place, shape preserved
#             fps_id=12,
#             api_name="/video"
#         )

#         raw_path = extract_video_path(result)

#         if raw_path:
#             raw_filename = f"{name}_temp.mp4"
#             final_filename = f"{name}_4s_reel.mp4"
#             shutil.copy(raw_path, raw_filename)

#             try:
#                 print(f"📏 Step 2: Applying sharp professional effects...")

#                 clip = VideoFileClip(raw_filename)

#                 # ✅ Seamless mirror loop: Forward + Reverse = 4-5 seconds
#                 reversed_clip = clip.transform(
#                     lambda get_frame, t: get_frame(clip.duration - t)
#                 )
#                 long_clip = concatenate_videoclips([clip, reversed_clip])
#                 total_dur = long_clip.duration

#                 # ✅ 9:16 Vertical Format (Instagram/TikTok/Reels ready)
#                 target_w, target_h = 1080, 1920

#                 # ✅ Apply sharp zoom + drift (NO blur — crop method)
#                 final_clip = long_clip.transform(
#                     lambda get_frame, t: make_sharp_zoom_frame(
#                         get_frame, t, total_dur, target_w, target_h
#                     ),
#                     apply_to="video"
#                 )

#                 # ✅ Force correct output size
#                 final_clip = final_clip.resized((target_w, target_h))

#                 print(f"🎬 Step 3: Rendering sharp professional video...")
#                 final_clip.write_videofile(
#                     final_filename,
#                     fps=24,
#                     codec="libx264",
#                     audio=False,
#                     ffmpeg_params=["-crf", "18"]  # ✅ Near-lossless quality
#                 )

#                 clip.close()
#                 if os.path.exists(raw_filename):
#                     os.remove(raw_filename)

#                 print(f"\n✅ SUCCESS! Professional powder video ready: {final_filename}")
#                 print(f"   📌 NO blur | Sharp LANCZOS zoom | Sponge intact | Shape preserved")

#             except Exception as e:
#                 print(f"⚠️ Video processing failed: {e}")

#     except Exception as e:
#         if "quota" in str(e).lower():
#             print(f"🛑 Quota reached. Wait 24h and retry.")
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
from moviepy import VideoFileClip, ColorClip, CompositeVideoClip, concatenate_videoclips, ImageClip
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np

# --- 1. SETUP & AUTHENTICATION ---
MY_TOKEN = "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"

# ✅ Powder Image Path
MY_PRODUCTS = {
    "emani_powder": r"images_datasets\powder_image_dataset\WhatsApp Image 2026-02-24 at 11.04.11 PM (1).jpeg",
}

# ✅ Server Connection
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

# --- 2. SAFE PATH EXTRACTION ---
def extract_video_path(result):
    if isinstance(result, dict):
        return result.get('video') or result.get('name')
    if isinstance(result, (list, tuple)):
        first_item = result[0]
        return first_item.get('video') if isinstance(first_item, dict) else first_item
    return result

# ✅ PURE SHARP FRAME MAKER — No AI distortion, all effects done manually
def make_sharp_professional_frame(original_img, t, total_dur, target_w, target_h):
    """
    Takes the ORIGINAL unchanged image every single frame.
    Applies zoom + drift purely through crop math.
    AI never touches the pixels — zero distortion.
    """
    orig_w, orig_h = original_img.size

    # ✅ Ken Burns: smooth zoom in → zoom out
    half = total_dur / 2
    if t <= half:
        zoom = 1.0 + 0.05 * (t / half)           # 1.0 → 1.05
    else:
        zoom = 1.05 - 0.05 * ((t - half) / half)  # 1.05 → 1.0

    # ✅ CROP center (not resize) — pixels stay 100% sharp
    crop_w = int(orig_w / zoom)
    crop_h = int(orig_h / zoom)
    left   = (orig_w - crop_w) // 2
    top    = (orig_h - crop_h) // 2
    cropped = original_img.crop((left, top, left + crop_w, top + crop_h))

    # ✅ LANCZOS — sharpest upscale
    sharp = cropped.resize((orig_w, orig_h), Image.LANCZOS)

    # ✅ Soft premium background for powder compact
    canvas = Image.new("RGB", (target_w, target_h), (238, 238, 240))

    paste_x = (target_w - orig_w) // 2
    paste_y = (target_h - orig_h) // 2

    # ✅ Gentle studio drift — product barely moves, very professional
    drift_x = int(18 * math.sin(2 * math.pi * t / total_dur))
    drift_y = int(7  * math.sin(4 * math.pi * t / total_dur))

    final_x = paste_x + drift_x
    final_y = paste_y + drift_y

    canvas.paste(sharp, (final_x, final_y))
    return np.array(canvas)


# --- 3. PROFESSIONAL POWDER VIDEO FUNCTION ---
def generate_stable_video(name, image_path):

    if not video_client:
        print("❌ No server connected. Please retry in 5 minutes.")
        return

    print(f"\n✨ Starting Professional Product Video for: {name.upper()}")

    if not os.path.exists(image_path):
        print(f"❌ Error: File NOT found at: {image_path}")
        return

    print(f"✅ Image found: {image_path}")

    try:
        print(f"🚀 Step 1: Generating AI Base Video (minimum motion)...")

        result = video_client.predict(
            image=handle_file(image_path),
            seed=42,
            randomize_seed=False,
            motion_bucket_id=1,   # ✅ MINIMUM — AI does almost nothing to the image
                                   #    All professional motion added by us in Step 2
            fps_id=12,
            api_name="/video"
        )

        raw_path = extract_video_path(result)

        if raw_path:
            raw_filename = f"{name}_temp.mp4"
            final_filename = f"{name}_4s_reel.mp4"
            shutil.copy(raw_path, raw_filename)

            try:
                print(f"📏 Step 2: Building professional video from ORIGINAL image...")

                # ✅ Load ORIGINAL image — this never gets distorted
                original_img = Image.open(image_path).convert("RGB")

                # ✅ Resize original to fit nicely in 9:16 frame
                target_w, target_h = 1080, 1920
                max_product_w = 900
                max_product_h = 900
                original_img.thumbnail((max_product_w, max_product_h), Image.LANCZOS)

                # ✅ Get AI video duration for timing reference
                ai_clip = VideoFileClip(raw_filename)
                ai_duration = ai_clip.duration
                ai_clip.close()

                # ✅ Total video = 4-5 seconds (forward + reverse loop)
                total_dur = ai_duration * 2
                fps = 24

                print(f"   Original image size: {original_img.size}")
                print(f"   Total video duration: {total_dur:.1f}s")

                # ✅ Build every frame from the ORIGINAL sharp image
                frames = []
                total_frames = int(total_dur * fps)

                print(f"   Building {total_frames} sharp frames...")
                for i in range(total_frames):
                    t = i / fps
                    frame = make_sharp_professional_frame(
                        original_img, t, total_dur, target_w, target_h
                    )
                    frames.append(frame)

                # ✅ Convert frames to video clip
                def make_frame(t):
                    idx = min(int(t * fps), len(frames) - 1)
                    return frames[idx]

                from moviepy import VideoClip
                final_clip = VideoClip(make_frame, duration=total_dur)

                print(f"🎬 Step 3: Rendering sharp professional video...")
                final_clip.write_videofile(
                    final_filename,
                    fps=fps,
                    codec="libx264",
                    audio=False,
                    ffmpeg_params=["-crf", "18"]  # ✅ Near-lossless quality
                )

                if os.path.exists(raw_filename):
                    os.remove(raw_filename)

                print(f"\n✅ SUCCESS! Professional powder video ready: {final_filename}")
                print(f"   📌 ZERO AI distortion | Original image used | Sponge intact | Shape 100% preserved")

            except Exception as e:
                print(f"⚠️ Video processing failed: {e}")
                import traceback
                traceback.print_exc()

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