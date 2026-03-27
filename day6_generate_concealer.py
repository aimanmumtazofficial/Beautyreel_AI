import time
from gradio_client import Client, handle_file
import shutil
import os

# --- 1. SETUP & AUTHENTICATION ---
# ⚠️ Use your active token from a fresh account
MY_TOKEN = "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"

# Mapping: Ensuring we use the correct image for concealer
# Updated path according to provided relative path
MY_PRODUCTS = {
    "lumina_concealer": r"images_datasets\concelar_image_dataset\Gemini_Generated_Image_bna37jbna37jbna3.png", # Relative path of concealer image
}

try:
    # Connecting to Stability AI for high-quality, stable results
    video_client = Client("stabilityai/stable-video-diffusion", token=MY_TOKEN)
except Exception as e:
    print(f"Warning: stabilityai server busy, using backup. Error: {e}")
    video_client = Client("multimodalart-stable-video-diffusion.hf.space", token=MY_TOKEN)

# --- 2. SAFE PATH EXTRACTION ---
def extract_video_path(result):
    """Deep search for the video file path in the AI response."""
    if isinstance(result, dict):
        return result.get('video') or result.get('name')
    if isinstance(result, (list, tuple)):
        first_item = result[0]
        return first_item.get('video') if isinstance(first_item, dict) else first_item
    return result

# --- 3. THE "PERFECT RESULT" FUNCTION ---
def generate_stable_video(name, image_path):
    print(f"\n🌸 Starting Professional Video Generation for: {name.upper()}")
    
    # Pre-check: Ensure image path is valid before spending quota
    if not os.path.exists(image_path):
        print(f"❌ Error: Concealer image NOT found at: {image_path}")
        print("Please check the relative path and folder structure.")
        return

    try:
        print(f"🚀 Processing image from: {image_path}... This may take 2-4 minutes.")
        
        # --- KEY SETTINGS FOR NO DISTORTION ---
        # motion_bucket_id=30: Keeps concealer bottle, applicator, and text 100% stable
        # fps_id=12: Smooth frame rate standard for this model
        result = video_client.predict(
            image=handle_file(image_path),
            seed=42,
            randomize_seed=False,
            motion_bucket_id=30, # Lower value = higher structural integrity and fewer artifacts
            fps_id=12,
            api_name="/video"
        )

        raw_path = extract_video_path(result)
        if raw_path:
            raw_filename = f"{name}_raw.mp4"
            final_filename = f"{name}_reels.mp4"
            
            # Copy to current working directory
            shutil.copy(raw_path, raw_filename)
            print(f"✅ Raw Video saved successfully: {raw_filename}")
            
            # --- PHASE 2: REELS CONVERSION (OPTIONAL) ---
            try:
                print(f"📏 Converting {raw_filename} to vertical 9:16 Reels format...")
                # Note: moviepy must be installed (`pip install moviepy`)
                from moviepy.editor import VideoFileClip, ColorClip, CompositeVideoClip
                clip = VideoFileClip(raw_filename)
                target_w, target_h = 1080, 1920
                scale = target_w / clip.w
                resized = clip.resize(scale)
                background = ColorClip(size=(target_w, target_h), color=(0, 0, 0), duration=clip.duration)
                final = CompositeVideoClip([background, resized.set_position(("center", "center"))])
                final.write_videofile(final_filename, fps=24, codec="libx264", audio=False)
                clip.close()
                
                # Cleanup: Remove temporary raw file
                if os.path.exists(raw_filename):
                    os.remove(raw_filename)
                print(f"🗑️ Temporary raw file removed.")
                
                print(f"\n✅ SUCCESS! Perfect video is ready: {final_filename}")
                print(f"🎥 Check the generated file in your project folder.")
                
            except Exception as e:
                # If moviepy fails, raw video is still preserved
                print(f"⚠️ Reels Conversion failed, but raw horizontal video is preserved: {e}")
            
    except Exception as e:
        error_msg = str(e)
        if "Quota" in error_msg.lower():
            print(f"🛑 Error: Quota reached for this account. Cannot complete")
        else:
            print(f"❌ System Error: {e}")

# --- 4. EXECUTION ---
if __name__ == "__main__":
    print("✨ --- BeautyReel AI: Single Concealer Processing --- ✨")
    # Loop over the dictionary, though it only contains one item now
    for product_name, path in MY_PRODUCTS.items():
        generate_stable_video(product_name, path)