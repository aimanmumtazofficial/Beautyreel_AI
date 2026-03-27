import time
from gradio_client import Client, handle_file
import shutil
import os
from moviepy import VideoFileClip, ColorClip, CompositeVideoClip, concatenate_videoclips

# --- 1. SETUP & AUTHENTICATION ---
MY_TOKEN = "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"

# Dictionary for Concealer
MY_PRODUCTS = {
    "luxury_concealer": r"images_datasets\concelar_image_dataset\Gemini_Generated_Image_bna37jbna37jbna3.png",
}

try:
    video_client = Client("stabilityai/stable-video-diffusion", token=MY_TOKEN)
except Exception as e:
    print(f"Warning: Server busy, using backup. Error: {e}")
    video_client = Client("multimodalart-stable-video-diffusion.hf.space", token=MY_TOKEN)

# --- 2. SAFE PATH EXTRACTION ---
def extract_video_path(result):
    if isinstance(result, dict):
        return result.get('video') or result.get('name')
    if isinstance(result, (list, tuple)):
        first_item = result[0]
        return first_item.get('video') if isinstance(first_item, dict) else first_item
    return result

# --- 3. THE GENERATION & STRETCHING FUNCTION ---
def generate_stable_video(name, image_path):
    print(f"\n✨ Starting 4-5 Second Video for: {name.upper()}")
    
    if not os.path.exists(image_path):
        print(f"❌ Error: File NOT found at: {image_path}")
        return

    try:
        print(f"🚀 Step 1: Generating AI Motion...")
        
        result = video_client.predict(
            image=handle_file(image_path),
            seed=42,
            randomize_seed=False,
            motion_bucket_id=40, 
            fps_id=12,
            api_name="/video"
        )

        raw_path = extract_video_path(result)
        if raw_path:
            raw_filename = f"{name}_temp.mp4"
            final_filename = f"{name}_4s_reel.mp4"
            shutil.copy(raw_path, raw_filename)
            
            # --- PHASE 2: STRETCH TO 4+ SECONDS & FORMAT 9:16 ---
            try:
                print(f"📏 Step 2: Stretching duration and formatting to 9:16...")
                
                # Load the 2-second clip
                clip = VideoFileClip(raw_filename)
                
                # Create the Reverse Clip (Manual Reverse for stability)
                reversed_clip = clip.transform(lambda get_frame, t: get_frame(clip.duration - t))
                
                # Combine Forward + Backward = 4 to 5 seconds total
                long_clip = concatenate_videoclips([clip, reversed_clip])
                
                # Vertical Setup
                target_w, target_h = 1080, 1920
                resized = long_clip.resized(width=target_w)
                
                # White Background (Premium for Concealers)
                background = ColorClip(size=(target_w, target_h), color=(255, 255, 255)).with_duration(long_clip.duration)
                
                # Final Composition
                final = CompositeVideoClip([background, resized.with_position("center")])
                
                print(f"🎬 Step 3: Rendering final file...")
                final.write_videofile(final_filename, fps=24, codec="libx264", audio=False)
                
                # Cleanup
                clip.close()
                if os.path.exists(raw_filename):
                    os.remove(raw_filename)
                    
                print(f"\n✅ SUCCESS! Your 4-second {name} video is ready: {final_filename}")
                
            except Exception as e:
                print(f"⚠️ Video processing failed: {e}")
            
    except Exception as e:
        if "quota" in str(e).lower():
            print(f"🛑 Error: Quota reached. Wait for 24h reset.")
        else:
            print(f"❌ AI Error: {e}")

# --- 4. EXECUTION ---
if __name__ == "__main__":
    for product_name, path in MY_PRODUCTS.items():
        generate_stable_video(product_name, path)