

# # # # ============================================================
# # # # BeautyReel AI - Complete Project Code
# # # # Generates UGC-style promotional videos for makeup products
# # # # ============================================================

# # # from gradio_client import Client, handle_file
# # # from anthropic import Anthropic
# # # import shutil
# # # import os

# # # # ── Clients ──────────────────────────────────────────────────
# # # video_client = Client("multimodalart/stable-video-diffusion")
# # # llm_client   = Anthropic()

# # # # ─────────────────────────────────────────────────────────────
# # # # FEATURE 1 — Product-Based Video Generation
# # # # Sends your image AS-IS (no modifications whatsoever)
# # # # ─────────────────────────────────────────────────────────────
# # # def extract_video_path(result):
# # #     """Safely parse Gradio's output regardless of format."""
# # #     if isinstance(result, (list, tuple)):
# # #         first = result[0]
# # #         if isinstance(first, dict) and 'video' in first:
# # #             return first['video']
# # #         elif isinstance(first, str):
# # #             return first
# # #     elif isinstance(result, dict) and 'video' in result:
# # #         return result['video']
# # #     raise ValueError(f"Unexpected result format: {result}")


# # # def generate_product_video(image_path, motion_level=50, output_name="output_video.mp4"):
# # #     """
# # #     FEATURE 1: Generates animated video from a static product image.
# # #     - image_path   : path to YOUR image (never modified)
# # #     - motion_level : 25=subtle | 50=moderate | 75=dynamic
# # #     - output_name  : name for the saved .mp4 file
# # #     """
# # #     print(f"🎬 Generating video for: {image_path}")

# # #     result = video_client.predict(
# # #         image=handle_file(image_path),   # ✅ original image sent as-is
# # #         seed=42,
# # #         randomize_seed=False,
# # #         motion_bucket_id=motion_level,
# # #         fps_id=15,
# # #         api_name="/video"
# # #     )

# # #     video_path = extract_video_path(result)
# # #     shutil.copy(video_path, output_name)
# # #     print(f"✅ Video saved → {output_name}")
# # #     return output_name


# # # # ─────────────────────────────────────────────────────────────
# # # # FEATURE 2 — Prompt-Based Customization
# # # # Lets the user describe background, lighting, model, theme
# # # # ─────────────────────────────────────────────────────────────
# # # def build_video_prompt(
# # #     product_name,
# # #     background_style="clean white studio",
# # #     lighting="soft ring light",
# # #     model_appearance="neutral, no model",
# # #     makeup_theme="natural glam"
# # # ):
# # #     """
# # #     FEATURE 2: Combines user inputs into a structured AI prompt.
# # #     Used for image-to-video guidance or future txt2img pipeline.
# # #     """
# # #     prompt = (
# # #         f"A premium promotional video of {product_name}. "
# # #         f"Background: {background_style}. "
# # #         f"Lighting: {lighting}. "
# # #         f"Model: {model_appearance}. "
# # #         f"Makeup theme: {makeup_theme}. "
# # #         f"Style: UGC aesthetic, Instagram Reels format, cinematic quality."
# # #     )
# # #     print(f"📝 Prompt built: {prompt}")
# # #     return prompt


# # # # ─────────────────────────────────────────────────────────────
# # # # FEATURE 3 — Social-Media-Ready Output
# # # # Converts video to vertical 9:16 for Reels / TikTok
# # # # Requires: pip install moviepy
# # # # ─────────────────────────────────────────────────────────────
# # # def convert_to_reels_format(input_video, output_video="reels_output.mp4"):
# # #     """
# # #     FEATURE 3: Converts any video to vertical 9:16 (1080x1920)
# # #     ready for Instagram Reels, TikTok, and Facebook Ads.
# # #     """
# # #     try:
# # #         from moviepy.editor import VideoFileClip, ColorClip, CompositeVideoClip

# # #         clip        = VideoFileClip(input_video)
# # #         target_w    = 1080
# # #         target_h    = 1920
# # #         scale       = min(target_w / clip.w, target_h / clip.h)
# # #         resized     = clip.resize(scale)

# # #         background  = ColorClip(size=(target_w, target_h), color=(0, 0, 0), duration=clip.duration)
# # #         x_pos       = (target_w  - resized.w) // 2
# # #         y_pos       = (target_h  - resized.h) // 2
# # #         final       = CompositeVideoClip([background, resized.set_position((x_pos, y_pos))])

# # #         final.write_videofile(output_video, fps=30, codec="libx264", audio=False)
# # #         print(f"✅ Reels-ready video saved → {output_video}")
# # #         return output_video

# # #     except ImportError:
# # #         print("⚠️  moviepy not installed. Run: pip install moviepy")
# # #         return input_video


# # # # ─────────────────────────────────────────────────────────────
# # # # FEATURE 4 — AI-Generated Marketing Captions (Claude LLM)
# # # # ─────────────────────────────────────────────────────────────
# # # def generate_caption(product_name, platform="Instagram", tone="trendy and engaging"):
# # #     """
# # #     FEATURE 4: Uses Claude to generate marketing captions + ad copy.
# # #     - platform : Instagram | TikTok | Facebook
# # #     - tone     : trendy | luxury | playful | bold
# # #     """
# # #     print(f"✍️  Generating caption for {product_name} on {platform}...")

# # #     response = llm_client.messages.create(
# # #         model="claude-sonnet-4-6",
# # #         max_tokens=400,
# # #         messages=[{
# # #             "role": "user",
# # #             "content": (
# # #                 f"Write a {tone} social media caption for a {product_name} promotional video "
# # #                 f"on {platform}. Include: 1 punchy hook line, 2-3 sentences of product hype, "
# # #                 f"a call-to-action, and 5 relevant hashtags. Keep it under 150 words."
# # #             )
# # #         }]
# # #     )

# # #     caption = response.content[0].text
# # #     print(f"\n📣 Generated Caption:\n{caption}\n")
# # #     return caption


# # # # ─────────────────────────────────────────────────────────────
# # # # MASTER PIPELINE — Runs all 4 features in one call
# # # # ─────────────────────────────────────────────────────────────
# # # def beautyReel_pipeline(
# # #     image_path,
# # #     product_name,
# # #     platform="Instagram",
# # #     background_style="clean white studio",
# # #     lighting="soft ring light",
# # #     model_appearance="neutral, no model",
# # #     makeup_theme="natural glam",
# # #     motion_level=50,
# # #     tone="trendy and engaging"
# # # ):
# # #     print("\n🌸 ─── BeautyReel AI Pipeline Starting ───────────────")

# # #     # Step 1 — Generate raw video (original image, untouched)
# # #     raw_video = generate_product_video(
# # #         image_path,
# # #         motion_level=motion_level,
# # #         output_name=f"{product_name}_raw.mp4"
# # #     )

# # #     # Step 2 — Build customization prompt (logged / future use)
# # #     build_video_prompt(product_name, background_style, lighting, model_appearance, makeup_theme)

# # #     # Step 3 — Convert to Reels format
# # #     final_video = convert_to_reels_format(raw_video, output_video=f"{product_name}_reels.mp4")

# # #     # Step 4 — Generate AI caption
# # #     caption = generate_caption(product_name, platform=platform, tone=tone)

# # #     # Save caption to .txt
# # #     caption_file = f"{product_name}_caption.txt"
# # #     with open(caption_file, "w", encoding="utf-8") as f:
# # #         f.write(caption)

# # #     print("✨ ─── BeautyReel AI Complete ────────────────────────")
# # #     print(f"   🎥 Video  : {final_video}")
# # #     print(f"   📝 Caption: {caption_file}")
# # #     print("─────────────────────────────────────────────────────\n")

# # #     return final_video, caption


# # # # ─────────────────────────────────────────────────────────────
# # # # ✅ RUN IT — Paste your image path below
# # # # ─────────────────────────────────────────────────────────────
# # # if __name__ == "__main__":
# # #     beautyReel_pipeline(
# # #         image_path     ="test_makeup_1.jpg.jpeg",  # 👈 YOUR IMAGE PATH
# # #         product_name   = "lipstick",
# # #         platform       = "Instagram",
# # #         background_style = "soft pink gradient",
# # #         lighting         = "golden hour glow",
# # #         model_appearance = "neutral, no model",
# # #         makeup_theme     = "bold red glam",
# # #         motion_level     = 50,
# # #         tone             = "trendy and luxurious"
# # #     )






# # # # ============================================================
# # # # BeautyReel AI - Complete Project Code (FIXED)
# # # # ✅ FIX: motion_bucket_id lowered to 15 — product stays EXACTLY
# # # #         as it is in your image. No extra lipsticks, no morphing.
# # # # ============================================================

# # from gradio_client import Client, handle_file
# # from anthropic import Anthropic
# # import shutil
# # import os

# # # ── Clients ──────────────────────────────────────────────────
# # video_client = Client("multimodalart/stable-video-diffusion")
# # llm_client   = Anthropic()

# # # ─────────────────────────────────────────────────────────────
# # # FEATURE 1 — Product-Based Video Generation
# # # ─────────────────────────────────────────────────────────────
# # def extract_video_path(result):
# #     """Safely parse Gradio's output regardless of format."""
# #     if isinstance(result, (list, tuple)):
# #         first = result[0]
# #         if isinstance(first, dict) and 'video' in first:
# #             return first['video']
# #         elif isinstance(first, str):
# #             return first
# #     elif isinstance(result, dict) and 'video' in result:
# #         return result['video']
# #     raise ValueError(f"Unexpected result format: {result}")


# # def generate_product_video(image_path, output_name="output_video.mp4"):
# #     """
# #     FEATURE 1: Generates animated video from a static product image.

# #     ✅ KEY FIX — motion_bucket_id=15
# #     ─────────────────────────────────
# #     OLD (broken): motion_bucket_id=50  → AI was adding extra objects
# #                                          e.g. extra lipstick appearing on cup
# #     NEW (fixed) : motion_bucket_id=15  → Product stays 100% unchanged.
# #                                          Only subtle shimmer/light animates.
    
# #     Rule: Keep motion_bucket_id between 10–20 for makeup products.
# #     Never go above 30 or product will start morphing/duplicating.
# #     """
# #     print(f"🎬 Generating video for: {image_path}")

# #     result = video_client.predict(
# #         image=handle_file(image_path),
# #         seed=42,                   # Fixed seed = same result every time
# #         randomize_seed=False,
# #         motion_bucket_id=15,       # ✅ FIXED: was 50, now 15 → no morphing
# #         fps_id=10,                 # ✅ FIXED: was 15, now 10 → smoother for still products
# #         api_name="/video"
# #     )

# #     video_path = extract_video_path(result)
# #     shutil.copy(video_path, output_name)
# #     print(f"✅ Video saved → {output_name}")
# #     return output_name


# # # ─────────────────────────────────────────────────────────────
# # # FEATURE 2 — Prompt-Based Customization
# # # ─────────────────────────────────────────────────────────────
# # def build_video_prompt(
# #     product_name,
# #     background_style="clean white studio",
# #     lighting="soft ring light",
# #     model_appearance="neutral, no model",
# #     makeup_theme="natural glam"
# # ):
# #     """
# #     FEATURE 2: Combines user inputs into a structured AI prompt.
# #     """
# #     prompt = (
# #         f"A premium promotional video of {product_name}. "
# #         f"Background: {background_style}. "
# #         f"Lighting: {lighting}. "
# #         f"Model: {model_appearance}. "
# #         f"Makeup theme: {makeup_theme}. "
# #         f"Style: UGC aesthetic, Instagram Reels format, cinematic quality."
# #     )
# #     print(f"📝 Prompt built: {prompt}")
# #     return prompt


# # # ─────────────────────────────────────────────────────────────
# # # FEATURE 3 — Social-Media-Ready Output (9:16 Reels Format)
# # # ─────────────────────────────────────────────────────────────
# # def convert_to_reels_format(input_video, output_video="reels_output.mp4"):
# #     """
# #     FEATURE 3: Converts any video to vertical 9:16 (1080x1920)
# #     ready for Instagram Reels, TikTok, and Facebook Ads.
# #     """
# #     try:
# #         from moviepy.editor import VideoFileClip, ColorClip, CompositeVideoClip

# #         clip        = VideoFileClip(input_video)
# #         target_w    = 1080
# #         target_h    = 1920
# #         scale       = min(target_w / clip.w, target_h / clip.h)
# #         resized     = clip.resize(scale)

# #         background  = ColorClip(size=(target_w, target_h), color=(0, 0, 0), duration=clip.duration)
# #         x_pos       = (target_w  - resized.w) // 2
# #         y_pos       = (target_h  - resized.h) // 2
# #         final       = CompositeVideoClip([background, resized.set_position((x_pos, y_pos))])

# #         final.write_videofile(output_video, fps=30, codec="libx264", audio=False)
# #         print(f"✅ Reels-ready video saved → {output_video}")
# #         return output_video

# #     except ImportError:
# #         print("⚠️  moviepy not installed. Run: pip install moviepy")
# #         return input_video


# # # ─────────────────────────────────────────────────────────────
# # # FEATURE 4 — AI-Generated Marketing Captions (Claude LLM)
# # # ─────────────────────────────────────────────────────────────
# # def generate_caption(product_name, platform="Instagram", tone="trendy and engaging"):
# #     """
# #     FEATURE 4: Uses Claude to generate marketing captions + ad copy.
# #     """
# #     print(f"✍️  Generating caption for {product_name} on {platform}...")

# #     response = llm_client.messages.create(
# #         model="claude-sonnet-4-6",
# #         max_tokens=400,
# #         messages=[{
# #             "role": "user",
# #             "content": (
# #                 f"Write a {tone} social media caption for a {product_name} promotional video "
# #                 f"on {platform}. Include: 1 punchy hook line, 2-3 sentences of product hype, "
# #                 f"a call-to-action, and 5 relevant hashtags. Keep it under 150 words."
# #             )
# #         }]
# #     )

# #     caption = response.content[0].text
# #     print(f"\n📣 Generated Caption:\n{caption}\n")
# #     return caption


# # # ─────────────────────────────────────────────────────────────
# # # MASTER PIPELINE — Runs all 4 features in one call
# # # ─────────────────────────────────────────────────────────────
# # def beautyReel_pipeline(
# #     image_path,
# #     product_name,
# #     platform="Instagram",
# #     background_style="clean white studio",
# #     lighting="soft ring light",
# #     model_appearance="neutral, no model",
# #     makeup_theme="natural glam",
# #     tone="trendy and engaging"
# # ):
# #     print("\n🌸 ─── BeautyReel AI Pipeline Starting ───────────────")

# #     # Step 1 — Generate raw video
# #     raw_video = generate_product_video(
# #         image_path,
# #         output_name=f"{product_name}_raw.mp4"
# #     )

# #     # Step 2 — Build customization prompt
# #     build_video_prompt(product_name, background_style, lighting, model_appearance, makeup_theme)

# #     # Step 3 — Convert to Reels format
# #     final_video = convert_to_reels_format(raw_video, output_video=f"{product_name}_reels.mp4")

# #     # Step 4 — Generate AI caption
# #     caption = generate_caption(product_name, platform=platform, tone=tone)

# #     # Save caption to .txt
# #     caption_file = f"{product_name}_caption.txt"
# #     with open(caption_file, "w", encoding="utf-8") as f:
# #         f.write(caption)

# #     print("✨ ─── BeautyReel AI Complete ────────────────────────")
# #     print(f"   🎥 Video  : {final_video}")
# #     print(f"   📝 Caption: {caption_file}")
# #     print("─────────────────────────────────────────────────────\n")

# #     return final_video, caption


# # # ─────────────────────────────────────────────────────────────
# # # ✅ RUN IT — 4 products, one by one
# # # ─────────────────────────────────────────────────────────────
# # if __name__ == "__main__":

# #     products = [
# #         {
# #             "image_path"      : "test_makeup_4.png",      # 👈 apna actual filename likhein
# #             "product_name"    : "lip_pencil",
# #             "background_style": "soft pink gradient",
# #             "lighting"        : "soft ring light",
# #             "makeup_theme"    : "everyday nude look",
# #             "tone"            : "trendy and luxurious"
# #         },
# #         {
# #             "image_path"      : "test_makeup_1.jpg.jpeg",         # 👈 apna actual filename likhein
# #             "product_name"    : "lipstick",
# #             "background_style": "rose gold bokeh",
# #             "lighting"        : "golden hour glow",
# #             "makeup_theme"    : "bold red glam",
# #             "tone"            : "bold and glamorous"
# #         },
# #         {
# #             "image_path"      : "test_makeup_2.jpg.jpeg",        # 👈 apna actual filename likhein
# #             "product_name"    : "concealer",
# #             "background_style": "clean white studio",
# #             "lighting"        : "natural daylight",
# #             "makeup_theme"    : "flawless skin finish",
# #             "tone"            : "fresh and natural"
# #         },
# #         {
# #             "image_path"      : "test_makeup_3.png",           # 👈 apna actual filename likhein
# #             "product_name"    : "powder",
# #             "background_style": "pastel lavender",
# #             "lighting"        : "soft diffused light",
# #             "makeup_theme"    : "matte perfection",
# #             "tone"            : "elegant and soft"
# #         },
# #     ]

# #     for p in products:
# #         beautyReel_pipeline(
# #             image_path       = p["image_path"],
# #             product_name     = p["product_name"],
# #             platform         = "Instagram",
# #             background_style = p["background_style"],
# #             lighting         = p["lighting"],
# #             makeup_theme     = p["makeup_theme"],
# #             tone             = p["tone"]
# #         )




# import time
# import shutil
# import os
# from gradio_client import Client, handle_file

# # --- 1. CONFIGURATION ---
# MY_TOKEN = "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"

# # Dictionary of your products and their image paths
# MY_PRODUCTS = {
#     "lipstick": "test_makeup_1.jpg.jpeg",
#     "concealer": "test_makeup_2.jpg.jpeg",
#     "powder": "test_makeup_3.png",
#     "lip_pencil": "test_makeup_4.png"
# }

# # Initialize Client
# try:
#     video_client = Client("stabilityai/stable-video-diffusion", token=MY_TOKEN)
# except:
#     video_client = Client("multimodalart/stable-video-diffusion", token=MY_TOKEN)

# # --- 2. HELPERS ---
# def extract_video_path(result):
#     if isinstance(result, dict):
#         return result.get('video') or result.get('name')
#     if isinstance(result, (list, tuple)):
#         first_item = result[0]
#         return first_item.get('video') if isinstance(first_item, dict) else first_item
#     return result

# def convert_to_reels_format(input_video, output_video):
#     print(f"📏 Converting {input_video} to vertical 9:16 format...")
#     try:
#         from moviepy.editor import VideoFileClip, ColorClip, CompositeVideoClip
#         clip = VideoFileClip(input_video)
#         target_w, target_h = 1080, 1920
#         scale = target_w / clip.w
#         resized = clip.resize(scale)
#         background = ColorClip(size=(target_w, target_h), color=(0, 0, 0), duration=clip.duration)
#         final = CompositeVideoClip([background, resized.set_position(("center", "center"))])
#         final.write_videofile(output_video, fps=24, codec="libx264", audio=False)
#         return output_video
#     except Exception as e:
#         print(f"⚠️ Reels Conversion skipped (MoviePy error): {e}")
#         return input_video

# # --- 3. CORE GENERATOR ---
# def process_beauty_product(name, image_path):
#     print(f"\n🌟 Starting Process for: {name.upper()}")
    
#     if not os.path.exists(image_path):
#         print(f"❌ Skipping: Image file '{image_path}' not found in folder.")
#         return

#     max_retries = 3
#     for attempt in range(max_retries):
#         try:
#             print(f"🎬 Attempt {attempt+1}: Generating video for {name}...")
            
#             # Predict using Stable Settings (Motion 40 for stability)
#             result = video_client.predict(
#                 image=handle_file(image_path),
#                 seed=42,
#                 randomize_seed=False,
#                 motion_bucket_id=40, 
#                 fps_id=12,
#                 api_name="/video"
#             )

#             raw_path = extract_video_path(result)
#             if raw_path:
#                 raw_name = f"{name}_raw.mp4"
#                 final_name = f"{name}_reels.mp4"
                
#                 shutil.copy(raw_path, raw_name)
#                 convert_to_reels_format(raw_name, final_name)
                
#                 print(f"✅ Finished {name}! File: {final_name}")
#                 return # Move to next product
            
#         except Exception as e:
#             if "Quota" in str(e):
#                 print(f"🛑 Quota reached for this account. Stop.")
#                 return "STOP"
#             print(f"⏳ Server Busy, waiting 60s... ({e})")
#             time.sleep(60)
    
#     print(f"❌ Failed to generate {name} after {max_retries} attempts.")

# # --- 4. EXECUTION ---
# if __name__ == "__main__":
#     print("🌸 --- BeautyReel AI: Multi-Product Batch Processing ---")
    
#     for product_name, path in MY_PRODUCTS.items():
#         status = process_beauty_product(product_name, path)
#         if status == "STOP":
#             break
            
#     print("\n✨ All tasks completed!")


import time
from gradio_client import Client, handle_file
import shutil
import os

# --- 1. SETUP & AUTHENTICATION ---
# Use your working token here
MY_TOKEN = "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"

# Mapping: Using your specific Relative Path for the lipstick image
MY_PRODUCTS = {
    "perfect_gold_lipstick": r"images_datasets\lipstick_image_dataset\pexels-solodsha-7664366.jpg",
}

try:
    # Connecting to Stability AI for high-quality, stable results
    video_client = Client("stabilityai/stable-video-diffusion", token=MY_TOKEN)
except Exception as e:
    print(f"Warning: stabilityai server busy, using backup. Error: {e}")
    video_client = Client("multimodalart-stable-video-diffusion.hf.space", token=MY_TOKEN)

# --- 2. SAFE PATH EXTRACTION ---
def extract_video_path(result):
    if isinstance(result, dict):
        return result.get('video') or result.get('name')
    if isinstance(result, (list, tuple)):
        first_item = result[0]
        return first_item.get('video') if isinstance(first_item, dict) else first_item
    return result

# --- 3. THE "PERFECT RESULT" FUNCTION ---
def generate_stable_video(name, image_path):
    print(f"\n🌸 Starting Professional Video for: {name.upper()}")
    
    # Check if the path is correct before starting
    if not os.path.exists(image_path):
        print(f"❌ Error: File NOT found at: {image_path}")
        print("Please check if the folder names are exactly correct.")
        return

    try:
        print(f"🚀 Processing image from: {image_path}")
        
        # --- MOTION SETTINGS FOR PRODUCT STABILITY ---
        # motion_bucket_id=30: Keeps the gold tube and cap from distorting
        result = video_client.predict(
            image=handle_file(image_path),
            seed=42,
            randomize_seed=False,
            motion_bucket_id=30, 
            fps_id=12,
            api_name="/video"
        )

        raw_path = extract_video_path(result)
        if raw_path:
            raw_filename = f"{name}_raw.mp4"
            final_filename = f"{name}_reels.mp4"
            
            shutil.copy(raw_path, raw_filename)
            print(f"✅ Raw Video saved: {raw_filename}")
            
            # --- PHASE 2: REELS CONVERSION ---
            try:
                print(f"📏 Converting to vertical 9:16 Reels format...")
                from moviepy.editor import VideoFileClip, ColorClip, CompositeVideoClip
                clip = VideoFileClip(raw_filename)
                target_w, target_h = 1080, 1920
                scale = target_w / clip.w
                resized = clip.resize(scale)
                background = ColorClip(size=(target_w, target_h), color=(0, 0, 0), duration=clip.duration)
                final = CompositeVideoClip([background, resized.set_position(("center", "center"))])
                final.write_videofile(final_filename, fps=24, codec="libx264", audio=False)
                clip.close()
                
                if os.path.exists(raw_filename):
                    os.remove(raw_filename)
                print(f"\n✅ SUCCESS! Perfect video is ready: {final_filename}")
            except Exception as e:
                print(f"⚠️ MoviePy conversion failed, but raw video is saved: {e}")
            
    except Exception as e:
        error_msg = str(e)
        if "Quota" in error_msg or "quota" in error_msg:
            print(f"🛑 Error: Quota reached. Please use a new account token.")
        else:
            print(f"❌ AI Error: {e}")

# --- 4. EXECUTION ---
if __name__ == "__main__":
    for product_name, path in MY_PRODUCTS.items():
        generate_stable_video(product_name, path)