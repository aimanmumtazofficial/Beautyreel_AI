# import tensorflow as tf
# from tensorflow.keras import layers, models
# import numpy as np
# import os

# # 1. Data Pipeline
# data_dir = "images_datasets"
# IMG_SIZE = (224, 224)
# BATCH_SIZE = 32

# train_ds = tf.keras.utils.image_dataset_from_directory(
#     data_dir, validation_split=0.2, subset="training", seed=123,
#     image_size=IMG_SIZE, batch_size=BATCH_SIZE)

# val_ds = tf.keras.utils.image_dataset_from_directory(
#     data_dir, validation_split=0.2, subset="validation", seed=123,
#     image_size=IMG_SIZE, batch_size=BATCH_SIZE)

# # 2. THE PROFESSIONAL BRAIN (Transfer Learning)
# # Using MobileNetV2 because it's an expert at recognizing objects
# base_model = tf.keras.applications.MobileNetV2(input_shape=(224, 224, 3),
#                                                include_top=False, 
#                                                weights='imagenet')
# base_model.trainable = False 

# # 3. Build the Beauty-Specific Layers
# model = models.Sequential([
#     base_model,
#     layers.GlobalAveragePooling2D(),
#     layers.Dense(128, activation='relu'),
#     layers.Dropout(0.2),
#     layers.Dense(4) # Raw output for 4 classes
# ])

# model.compile(optimizer='adam',
#               loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
#               metrics=['accuracy'])

# # 4. Train (Only 10-15 epochs needed for Transfer Learning)
# print("🚀 Training Professional Model...")
# model.fit(train_ds, validation_data=val_ds, epochs=15)
# model.save('beauty_model_final.keras')

# # 5. PREDICTION LOGIC (For Dashboard)
# def predict_product(image_pil):
#     # Resize
#     img = image_pil.resize((224, 224))
#     img_array = tf.keras.preprocessing.image.img_to_array(img)
    
#     # IMPORTANT: MobileNetV2 requires specific preprocessing
#     img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
    
#     img_array = np.expand_dims(img_array, axis=0)
#     predictions = model.predict(img_array)
#     score = tf.nn.softmax(predictions[0]).numpy()
    
#     # Exact Mapping based on your folders
#     my_folders = [
#         'concelar_image_dataset', 
#         'lip_pencil_image_dataset', 
#         'lipstick_image_dataset', 
#         'powder_image_dataset'
#     ]
    
#     result_idx = np.argmax(score)
#     return my_folders[result_idx], score[result_idx] * 100




import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
import os

# ==========================================
# PART 1: DATA PIPELINE
# ==========================================
data_dir = "images_datasets"
IMG_SIZE = (224, 224)
BATCH_SIZE = 32

# Load training dataset
train_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir, 
    validation_split=0.2, 
    subset="training", 
    seed=123,
    image_size=IMG_SIZE, 
    batch_size=BATCH_SIZE
)

# Load validation dataset
val_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir, 
    validation_split=0.2, 
    subset="validation", 
    seed=123,
    image_size=IMG_SIZE, 
    batch_size=BATCH_SIZE
)

# ==========================================
# PART 2: TRANSFER LEARNING SETUP
# ==========================================
# Using MobileNetV2 as the base expert brain
base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False, 
    weights='imagenet'
)
base_model.trainable = False 

# Building the final layers for your 4 beauty products
model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.2),
    layers.Dense(4) # Output layer for 4 classes (Logits)
])

# Compiling with 'from_logits=True'
model.compile(
    optimizer='adam',
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
    metrics=['accuracy']
)

# ==========================================
# PART 3: TRAINING & SAVING
# ==========================================
print("🚀 Training Professional Model (Transfer Learning)...")
model.fit(train_ds, validation_data=val_ds, epochs=15)

# Saving the final model
model.save('beauty_model_final.keras')
print("✅ Model saved as 'beauty_model_final.keras'")

# ==========================================
# PART 4: UPDATED PREDICTION LOGIC
# ==========================================
def predict_product(image_pil):
    """
    Predicts the makeup product from a PIL image.
    This section handles preprocessing and mapping specifically for MobileNetV2.
    """
    # STEP A: Resize image to 224x224 (Must match training dimensions)
    img = image_pil.resize((224, 224))
    
    # STEP B: Convert the image into a NumPy array
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    
    # STEP C: CRITICAL FIX (Essential for MobileNetV2)
    # Do NOT use manual division (like / 255.0). 
    # This function formats pixels exactly how MobileNetV2 expects them.
    img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
    
    # STEP D: Add Batch Dimension (Model expects input shape: [1, 224, 224, 3])
    img_array = np.expand_dims(img_array, axis=0)
    
    # STEP E: Execute Prediction
    predictions = model.predict(img_array)
    
    # STEP F: Convert raw output (logits) into probabilities (%)
    # Since the model uses 'from_logits=True', softmax is applied here for clarity.
    score = tf.nn.softmax(predictions[0]).numpy()
    
    # Exact Mapping (Follows the alphabetical order found in your directory)
    my_folders = [
        'concelar_image_dataset', 
        'lip_pencil_image_dataset', 
        'lipstick_image_dataset', 
        'powder_image_dataset'
    ]
    
    # Get the index of the highest probability
    result_idx = np.argmax(score)
    confidence = score[result_idx] * 100
    
    # Terminal Debugging: Check the percentage assigned to each category
    print(f"\n--- AI PREDICTION DEBUG ---")
    print(f"Scores: {dict(zip(my_folders, score))}")
    print(f"Detected: {my_folders[result_idx]} ({confidence:.2f}%)")
    
    return my_folders[result_idx], confidence