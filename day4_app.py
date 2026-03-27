import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import tensorflow as tf
import numpy as np
import os

# --- 1. SETUP & MODEL LOADING ---
MODEL_PATH = 'beauty_model_v3.keras'
model = tf.keras.models.load_model(MODEL_PATH)

# Automatically fetch class names from your dataset folders
DATA_DIR = "images_datasets"
class_names = sorted([f for f in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, f))])

# --- 2. PREDICTION LOGIC ---
def upload_and_predict():
    file_path = filedialog.askopenfilename()
    if not file_path:
        return

    # Update UI to show the selected image
    img = Image.open(file_path)
    img_thumbnail = img.resize((300, 300))
    img_display = ImageTk.PhotoImage(img_thumbnail)
    img_label.config(image=img_display)
    img_label.image = img_display 

    # AI Processing (Pre-processing for the Brain)
    test_img = tf.keras.preprocessing.image.load_img(file_path, target_size=(224, 224))
    img_array = tf.keras.preprocessing.image.img_to_array(test_img)
    img_array = np.expand_dims(img_array, axis=0)

    # Run Prediction
    predictions = model.predict(img_array)
    score = tf.nn.softmax(predictions[0])
    detected_class = class_names[np.argmax(score)]
    confidence = 100 * np.max(score)

    # Update Labels with results
    result_label.config(text=f"Product: {detected_class.title()}")
    conf_label.config(text=f"Confidence: {confidence:.2f}%")

# --- 3. LUXURY ROSE UI DESIGN ---
root = tk.Tk()
root.title("BeautyReel AI - Luxury Edition")
root.geometry("500x650")
root.configure(bg="#f9f9f9") # Pearl White Background

# Elegant Title
title = tk.Label(root, text="✨ BEAUTY SCANNER", bg="#f9f9f9", fg="#efadce", 
                 font=("Segoe UI", 24, "italic", "bold"))
title.pack(pady=35)

# Rose Pink Button
btn = tk.Button(root, text="Upload Makeup Photo", command=upload_and_predict, 
                padx=25, pady=12, bg="#efadce", fg="white", font=("Segoe UI", 11, "bold"),
                relief="raised", activebackground="#fce4ec", cursor="hand2")
btn.pack(pady=10)

# Image Display Area (with a slight border)
img_label = tk.Label(root, bg="#ffffff", highlightbackground="#efadce", highlightthickness=1)
img_label.pack(pady=20)

# Result Labels
result_label = tk.Label(root, text="Product: (Waiting...)", font=("Segoe UI", 18), 
                        bg="#f9f9f9", fg="#333333") # Dark Gray for readability
result_label.pack(pady=5)

conf_label = tk.Label(root, text="Confidence: 0%", font=("Segoe UI", 14), 
                      bg="#f9f9f9", fg="#d4af37") # Gold Accent for confidence
conf_label.pack()

# Footer
footer = tk.Label(root, text="Powered by BeautyReel AI Engine", font=("Segoe UI", 9), 
                  bg="#f9f9f9", fg="#bdc3c7")
footer.pack(side="bottom", pady=15)

root.mainloop()