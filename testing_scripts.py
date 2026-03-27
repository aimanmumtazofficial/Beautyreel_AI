


# import tensorflow as tf
# from tensorflow.keras.preprocessing import image
# import numpy as np
# import matplotlib.pyplot as plt
# import os

# # 1. Load your saved "Beauty Brain"
# # Make sure this file is in your BeautyReel_Project folder!
# model_path = 'beauty_model_v3.keras'
# if not os.path.exists(model_path):
#     print(f"❌ Error: {model_path} not found. Did you finish training?")
# else:
#     model = tf.keras.models.load_model(model_path)

# # 2. Setup your categories
# # IMPORTANT: These MUST be in alphabetical order to match how the AI learned them
# # Example: ['concealer', 'lipstick', 'mascara', 'powder']
# class_names = sorted(os.listdir('images_datasets')) 
# print(f"🔍 AI is checking against these categories: {class_names}")

# def predict_makeup(img_path):
#     if not os.path.exists(img_path):
#         print(f"❌ Error: Image '{img_path}' not found in the folder!")
#         return

#     # Load and resize to 224x224 (The size the AI was trained on)
#     img = image.load_img(img_path, target_size=(224, 224))
    
#     # Process the image for the AI
#     img_array = image.img_to_array(img)
#     img_array = np.expand_dims(img_array, axis=0) # Add a 'batch' dimension
    
#     # Make the prediction
#     predictions = model.predict(img_array)
#     score = tf.nn.softmax(predictions[0]) # Convert numbers to probabilities
    
#     # Get the winner
#     result_index = np.argmax(score)
#     result_class = class_names[result_index]
#     confidence = 100 * np.max(score)
    
#     print("-" * 30)
#     print(f"✨ RESULT: {result_class.upper()}")
#     print(f"📊 CONFIDENCE: {confidence:.2f}%")
#     print("-" * 30)
    
#     # Show the visual result
#     plt.imshow(img)
#     plt.title(f"Prediction: {result_class} ({confidence:.2f}%)")
#     plt.axis('off')
#     plt.show()

# # --- THE TEST ---
# # This looks for your file: test_makeup.jpg
# predict_makeup('test_makeup_1.jpg.jpeg')
# predict_makeup('test_makeup_2.jpg.jpeg')
# predict_makeup('test_makeup_3.png')
# predict_makeup('test_makeup_4.png')




import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import os

# ==========================================
# 1. LOAD THE SAVED MODEL
# ==========================================
# This refers to the file created after training ('beauty_model_final.keras')
model_path = 'beauty_model_final.keras'

if not os.path.exists(model_path):
    print(f"❌ Error: {model_path} not found. Please train the model first!")
else:
    model = tf.keras.models.load_model(model_path)
    print("✅ Professional Beauty Model Loaded Successfully!")

# ==========================================
# 2. CATEGORIES SETUP
# ==========================================
# These must remain in alphabetical order to match the dataset directory structure
class_names = [
    'concelar_image_dataset', 
    'lip_pencil_image_dataset', 
    'lipstick_image_dataset', 
    'powder_image_dataset'
]

def predict_makeup(img_path):
    if not os.path.exists(img_path):
        print(f"❌ Error: File '{img_path}' was not found in the directory!")
        return

    # STEP A: Load & Resize (Must match training dimensions: 224x224)
    img = tf.keras.utils.load_img(img_path, target_size=(224, 224))
    
    # STEP B: Convert to Array
    img_array = tf.keras.utils.img_to_array(img)
    
    # STEP C: Add Batch Dimension
    # The model expects an input shape of [1, 224, 224, 3]
    img_array = np.expand_dims(img_array, axis=0) 
    
    # Note: Preprocessing (preprocess_input) is now built into the model architecture, 
    # so manual scaling (like /255) is no longer required here.

    # STEP D: Make Prediction
    predictions = model.predict(img_array)
    
    # STEP E: Convert Logits to Probabilities (Softmax)
    score = tf.nn.softmax(predictions[0]).numpy()
    
    # Extract Results
    result_idx = np.argmax(score)
    result_class = class_names[result_idx]
    confidence = 100 * score[result_idx]
    
    # Print Results to Console
    print("\n" + "="*30)
    print(f"✨ AI PREDICTION: {result_class.replace('_image_dataset', '').upper()}")
    print(f"📊 CONFIDENCE: {confidence:.2f}%")
    print("="*30)
    
    # Visual Output Display
    plt.imshow(img)
    plt.title(f"{result_class}: {confidence:.2f}%")
    plt.axis('off')
    plt.show()

# ==========================================
# 3. TESTING (Verify your image filenames)
# ==========================================
# Ensure the file extensions (e.g., .jpg.jpeg) match your actual files
test_images = [
    'test_makeup_1.jpg.jpeg', 
    'test_makeup_2.jpg.jpeg', 
    'test_makeup_3.png', 
    'test_makeup_4.png'
]

for img in test_images:
    predict_makeup(img)