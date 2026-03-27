# # # from gradio_client import Client, handle_file
# # # import shutil
# # # import os

# # # # --- STEP 1: Connect with YOUR Token ---
# # # MY_TOKEN = "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" 

# # # try:
# # #     # Using 'token' for older client versions or 'hf_token' for new ones
# # #     client = Client("multimodalart/stable-video-diffusion", token=MY_TOKEN)
    
# # #     def generate_video_smit(image_path):
# # #         print(f"🎬 Phase 3: Processing {image_path}")
        
# # #         if not os.path.exists(image_path):
# # #             print(f"❌ Error: File '{image_path}' not found!")
# # #             return

# # #         print("🚀 Sending to AI Engine... This will take 2-4 minutes.")
        
# # #         # --- STEP 2: The Prediction ---
# # #         result = client.predict(
# # #             image=handle_file(image_path),
# # #             seed=42,
# # #             randomize_seed=False,
# # #             motion_bucket_id=127,
# # #             fps_id=6,
# # #             api_name="/video"
# # #         )
        
# # #         # --- STEP 3: DICTIONARY / TUPLE ERROR FIX ---
# # #         temp_video_path = None

# # #         # Agar result dictionary hai (Naya Update)
# # #         if isinstance(result, dict):
# # #             temp_video_path = result.get('video') or result.get('name') or result.get('data', [None])[0]
# # #         # Agar result tuple/list hai
# # #         elif isinstance(result, (tuple, list)):
# # #             first_val = result[0]
# # #             if isinstance(first_val, dict):
# # #                 temp_video_path = first_val.get('video') or first_val.get('name')
# # #             else:
# # #                 temp_video_path = first_val
# # #         # Agar result direct string hai
# # #         else:
# # #             temp_video_path = result

# # #         # --- STEP 4: Saving the Video ---
# # #         final_video_name = "generated_reel.mp4"
        
# # #         # 'temp_video_path' must be a string now
# # #         if temp_video_path and isinstance(temp_video_path, str) and os.path.exists(temp_video_path):
# # #             shutil.copy(temp_video_path, final_video_name)
# # #             print("\n" + "="*40)
# # #             print("✅ SUCCESS! Video Generated Successfully")
# # #             print(f"🎥 Your Reel is ready: {os.path.abspath(final_video_name)}")
# # #             print("="*40)
# # #         else:
# # #             print(f"❌ Error: Could not extract a valid file path from result: {result}")

# # #     # Run the generator
# # #     generate_video_smit("test_makeup_1.jpg.jpeg")

# # # except Exception as e:
# # #     print(f"❌ Error during AI generation: {e}")



# # from gradio_client import Client, handle_file
# # import shutil
# # import os

# # MY_TOKEN = "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" 

# # try:
# #     client = Client("multimodalart/stable-video-diffusion", token=MY_TOKEN)
    
# #     def generate_high_quality_video(image_path):
# #         print(f"🎬 Processing: {image_path}")
        
# #         # --- PREDICTION WITH QUALITY SETTINGS ---
# #         result = client.predict(
# #             image=handle_file(image_path),
# #             seed=42,
# #             randomize_seed=False,
# #             # MOTION BUCKET: 40-60 rakhein (Zyada karne se shape bigarrti hai)
# #             motion_bucket_id=50,   
# #             # FPS: 10-15 rakhein smoother video ke liye
# #             fps_id=12,             
# #             api_name="/video"
# #         )
        
# #         # Dictionary handling logic
# #         if isinstance(result, dict):
# #             temp_path = result.get('video') or result.get('name')
# #         elif isinstance(result, (list, tuple)):
# #             temp_path = result[0]
# #         else:
# #             temp_path = result

# #         if temp_path and os.path.exists(temp_path):
# #             shutil.copy(temp_path, "beauty_reel_fixed.mp4")
# #             print("\n" + "="*40)
# #             print("✅ SUCCESS! Optimized Video is Ready.")
# #             print("="*40)

# #     generate_high_quality_video("test_makeup_1.jpg.jpeg")

# # except Exception as e:
# #     print(f"❌ Error: {e}")


# import time
# from gradio_client import Client, handle_file
# import shutil
# import os

# # --- SETUP ---
# MY_TOKEN = "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"
# IMAGE_FILE = "test_makeup_1.jpg.jpeg"

# def generate_video_final(image_path):
#     try:
#         print(f"🎬 Processing: {image_path}")
#         client = Client("multimodalart/stable-video-diffusion", token=MY_TOKEN)
        
#         # --- PREDICTION ---
#         result = client.predict(
#             image=handle_file(image_path),
#             seed=42,
#             randomize_seed=False,
#             motion_bucket_id=50, # Product shape stable rakhne ke liye
#             fps_id=12,
#             api_name="/video"
#         )
        
#         # --- FIXING THE 'DICT' ERROR ---
#         temp_video_path = None

#         # Logic 1: Agar result khud aik dictionary hai
#         if isinstance(result, dict):
#             temp_video_path = result.get('video') or result.get('name')
        
#         # Logic 2: Agar result aik list/tuple hai (purana format)
#         elif isinstance(result, (list, tuple)):
#             first_item = result[0]
#             if isinstance(first_item, dict):
#                 temp_video_path = first_item.get('video') or first_item.get('name')
#             else:
#                 temp_video_path = first_item
        
#         # Logic 3: Agar result direct string hai
#         else:
#             temp_video_path = result

#         # --- SAVING THE FILE ---
#         if temp_video_path and isinstance(temp_video_path, str) and os.path.exists(temp_video_path):
#             final_output = "beauty_reel_success.mp4"
#             shutil.copy(temp_video_path, final_output)
#             print("\n" + "="*40)
#             print("✅ SUCCESS! Video Generated Successfully!")
#             print(f"🎥 File Saved: {os.path.abspath(final_output)}")
#             print("="*40)
#         else:
#             print(f"❌ Error: Result format not recognized. Result was: {result}")

#     except Exception as e:
#         error_msg = str(e)
#         if "No GPU" in error_msg:
#             print("⏳ Server Busy (GPU Queue Full). Please try again in 2-3 minutes.")
#         else:
#             print(f"❌ Unexpected Error: {error_msg}")

# # --- RUN ---
# generate_video_final(IMAGE_FILE)


import time
from gradio_client import Client, handle_file
import shutil
import os

# --- 1. SETTINGS ---
# Using your new fresh access token
MY_TOKEN = "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"
# Ensure this file exists in your project directory
IMAGE_FILE = "test_makeup_1.jpg.jpeg"

def generate_perfect_video(image_path):
    try:
        print(f"🎬 Processing: {image_path}")
        # Connecting to the official Stability AI engine for superior quality
        client = Client("stabilityai/stable-video-diffusion", token=MY_TOKEN)
        
        print("🚀 Sending to AI Engine... Estimated time: 2-4 minutes.")
        
        # --- 2. PREDICTION WITH STABLE SETTINGS ---
        result = client.predict(
            image=handle_file(image_path),
            seed=42,
            randomize_seed=False,
            # MOTION BUCKET: Set to 40 to maintain product structural integrity
            motion_bucket_id=40,   
            # FPS: Set to 12 for smooth video playback
            fps_id=12,             
            api_name="/video"
        )
        
        # --- 3. EXTRACT PATH (DICT/LIST FIX) ---
        # Handling the updated response format from the API
        temp_video_path = None
        if isinstance(result, dict):
            temp_video_path = result.get('video') or result.get('name')
        elif isinstance(result, (list, tuple)):
            first_item = result[0]
            temp_video_path = first_item.get('video') if isinstance(first_item, dict) else first_item
        else:
            temp_video_path = result

        # --- 4. SAVE FINAL REEL ---
        if temp_video_path and isinstance(temp_video_path, str) and os.path.exists(temp_video_path):
            final_output = "perfect_beauty_reel.mp4"
            shutil.copy(temp_video_path, final_output)
            print("\n" + "="*40)
            print("✅ SUCCESS! Video Generated Perfectly.")
            print(f"🎥 Location: {os.path.abspath(final_output)}")
            print("="*40)
        else:
            print(f"❌ Error: Result format issue. Received: {result}")

    except Exception as e:
        error_msg = str(e)
        if "Quota" in error_msg.lower():
            print("❌ Quota Error: Your new account has exceeded the free GPU limit.")
        elif "No GPU" in error_msg:
            print("⏳ Server Busy. Do NOT close the program; please wait 2 minutes and try again.")
        else:
            print(f"❌ Unexpected Error: {error_msg}")

# --- EXECUTION ---
if __name__ == "__main__":
    generate_perfect_video(IMAGE_FILE)