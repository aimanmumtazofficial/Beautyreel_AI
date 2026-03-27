# import tkinter as tk
# from PIL import Image, ImageTk
# import cv2
# import tensorflow as tf
# import numpy as np
# import os
 
# # --- 1. SETUP & MODEL LOADING ---
# # Using the PRO model you just trained for 98% accuracy!
# MODEL_PATH = 'beauty_model_pro.keras' 
# model = tf.keras.models.load_model(MODEL_PATH)

# # Automatically fetch class names from your dataset folders
# DATA_DIR = "images_datasets"
# class_names = sorted([f for f in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, f))])

# # --- [NEW] Stability History ---
# predictions_history = [] 

# cap = None # Global variable for the camera

# # --- 2. LIVE CAMERA LOGIC ---
# def start_camera():
#     global cap
#     if cap is None:
#         cap = cv2.VideoCapture(0) # Open your Dell's webcam
#     update_frame()

# def update_frame():
#     global predictions_history
#     ret, frame = cap.read()
#     if ret:
#         # 1. Flip for mirror effect and convert color for Tkinter
#         frame = cv2.flip(frame, 1)
#         cv2_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
#         # 2. AI Prediction Logic
#         ai_frame = cv2.resize(cv2_img, (224, 224))
#         img_array = np.expand_dims(ai_frame, axis=0)
        
#         # Predict
#         preds = model.predict(img_array, verbose=0)
#         score = tf.nn.softmax(preds[0])
#         detected_class = class_names[np.argmax(score)]
#         confidence = 100 * np.max(score)

#         # --- [NEW] Stability Patch Logic ---
#         predictions_history.append(detected_class)
#         # Keep only the last 10 frames to decide the label
#         if len(predictions_history) > 10: 
#             predictions_history.pop(0) 
        
#         # Pick the most frequent result from the last 10 frames
#         stable_result = max(set(predictions_history), key=predictions_history.count)

#         # 3. Update UI Text (Using the STABLE result)
#         result_label.config(text=f"Detected: {stable_result.title()}")
#         conf_label.config(text=f"Confidence: {confidence:.2f}%")

#         # 4. Update Video Feed on Screen
#         img_tk = Image.fromarray(cv2_img).resize((400, 300))
#         final_img = ImageTk.PhotoImage(image=img_tk)
#         video_label.imgtk = final_img
#         video_label.configure(image=final_img)

#     # Call this function again after 10ms
#     video_label.after(10, update_frame)

# # --- 3. LUXURY ROSE UI DESIGN ---
# root = tk.Tk()
# root.title("BeautyReel AI - Luxury Live Edition")
# root.geometry("600x800")
# root.configure(bg="#f9f9f9")

# # Elegant Title
# title = tk.Label(root, text="✨ LIVE BEAUTY SCANNER", bg="#f9f9f9", fg="#efadce", 
#                  font=("Segoe UI", 24, "italic", "bold"))
# title.pack(pady=20)

# # Live Video Display Area
# video_label = tk.Label(root, bg="#ffffff", highlightbackground="#efadce", highlightthickness=2)
# video_label.pack(pady=10)

# # Start Scan Button
# btn = tk.Button(root, text="START LIVE SCAN", command=start_camera, 
#                 padx=30, pady=12, bg="#efadce", fg="white", font=("Segoe UI", 12, "bold"),
#                 relief="raised", activebackground="#fce4ec", cursor="hand2")
# btn.pack(pady=20)

# # Result Labels
# result_label = tk.Label(root, text="Waiting for Camera...", font=("Segoe UI", 20), 
#                         bg="#f9f9f9", fg="#333333")
# result_label.pack(pady=5)

# conf_label = tk.Label(root, text="Confidence: 0%", font=("Segoe UI", 16), 
#                       bg="#f9f9f9", fg="#d4af37")
# conf_label.pack()

# # Clean shutdown
# def on_closing():
#     if cap:
#         cap.release()
#     root.destroy()

# root.protocol("WM_DELETE_WINDOW", on_closing)
# root.mainloop()




import tkinter as tk
from PIL import Image, ImageTk
import cv2
import tensorflow as tf
import numpy as np
import os

# --- 1. SETUP & MODEL LOADING ---
# Path exactly wahi rakhein jo aapki trained file ka naam hai
MODEL_PATH = 'beauty_model_pro.keras' 
model = tf.keras.models.load_model(MODEL_PATH)

# Dataset folder se classes fetch karna (Lipstick, Foundation, etc.)
DATA_DIR = "images_datasets"
class_names = sorted([f for f in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, f))])

# History list for visual stability
predictions_history = [] 
cap = None 

# --- 2. LIVE CAMERA LOGIC ---
def start_camera():
    global cap
    if cap is None:
        cap = cv2.VideoCapture(0) # Dell webcam default index
    update_frame()

def update_frame():
    global predictions_history
    ret, frame = cap.read()
    if ret:
        # Flip for mirror effect and convert BGR to RGB
        frame = cv2.flip(frame, 1)
        cv2_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # --- [CRITICAL UPDATE FOR MOBILENETV2] ---
        # 1. Resize to 224x224 (Standard for MobileNet)
        ai_frame = cv2.resize(cv2_img, (224, 224))
        
        # 2. Preprocessing: MobileNetV2 requires scaling pixels to [-1, 1]
        # Purane code mein ye missing tha, iske bagair accuracy drop ho jati hai
        img_array = tf.keras.applications.mobilenet_v2.preprocess_input(ai_frame)
        img_array = np.expand_dims(img_array, axis=0)
        
        # 3. Prediction
        preds = model.predict(img_array, verbose=0)
        
        # 4. Softmax Application (Since your model uses from_logits=True)
        score = tf.nn.softmax(preds[0])
        detected_class = class_names[np.argmax(score)]
        confidence = 100 * np.max(score)

        # --- Stability Patch Logic ---
        predictions_history.append(detected_class)
        if len(predictions_history) > 10: 
            predictions_history.pop(0) 
        
        # Pick the most stable result from the history
        stable_result = max(set(predictions_history), key=predictions_history.count)

        # Update UI Labels
        result_label.config(text=f"Detected: {stable_result.title()}")
        conf_label.config(text=f"Confidence: {confidence:.2f}%")

        # Update Live Feed on UI
        img_tk = Image.fromarray(cv2_img).resize((400, 300))
        final_img = ImageTk.PhotoImage(image=img_tk)
        video_label.imgtk = final_img
        video_label.configure(image=final_img)

    # Refresh every 10ms
    video_label.after(10, update_frame)

# --- 3. LUXURY UI DESIGN ---
root = tk.Tk()
root.title("BeautyReel AI - Luxury Live Edition")
root.geometry("600x800")
root.configure(bg="#f9f9f9")

# Professional English Header for Presentation
title = tk.Label(root, text="✨ LIVE BEAUTY SCANNER", bg="#f9f9f9", fg="#efadce", 
                 font=("Segoe UI", 24, "italic", "bold"))
title.pack(pady=20)

# Video Display Frame
video_label = tk.Label(root, bg="#ffffff", highlightbackground="#efadce", highlightthickness=2)
video_label.pack(pady=10)

# Professional Button
btn = tk.Button(root, text="START LIVE SCAN", command=start_camera, 
                padx=30, pady=12, bg="#efadce", fg="white", font=("Segoe UI", 12, "bold"),
                relief="raised", activebackground="#fce4ec", cursor="hand2")
btn.pack(pady=20)

# Results Display
result_label = tk.Label(root, text="Waiting for Camera...", font=("Segoe UI", 20), 
                        bg="#f9f9f9", fg="#333333")
result_label.pack(pady=5)

conf_label = tk.Label(root, text="Confidence: 0%", font=("Segoe UI", 16), 
                      bg="#f9f9f9", fg="#d4af37")
conf_label.pack()

# Application Shutdown Protocol
def on_closing():
    if cap:
        cap.release()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()