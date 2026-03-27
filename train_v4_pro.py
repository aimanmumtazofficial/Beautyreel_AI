# import tensorflow as tf
# from tensorflow.keras import layers, models

# # 1. Load Data (Same as before)
# img_size = (224, 224)
# batch_size = 32

# train_ds = tf.keras.utils.image_dataset_from_directory(
#     "images_datasets", validation_split=0.2, subset="training", seed=123,
#     image_size=img_size, batch_size=batch_size)

# val_ds = tf.keras.utils.image_dataset_from_directory(
#     "images_datasets", validation_split=0.2, subset="validation", seed=123,
#     image_size=img_size, batch_size=batch_size)

# # 2. THE SECRET SAUCE: Transfer Learning
# base_model = tf.keras.applications.MobileNetV2(input_shape=(224, 224, 3),
#                                                include_top=False, # Remove Google's labels
#                                                weights='imagenet') # Use Google's knowledge
# base_model.trainable = False # Don't change the "Expert" brain parts

# # 3. Build the "Beauty Expert" Layer on top
# model = models.Sequential([
#     base_model,
#     layers.GlobalAveragePooling2D(),
#     layers.Dense(128, activation='relu'),
#     layers.Dropout(0.2), # Prevents memorizing
#     layers.Dense(len(train_ds.class_names), activation='softmax')
# ])

# model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# # 4. Train (It will be MUCH faster now)
# model.fit(train_ds, validation_data=val_ds, epochs=10)

# # 5. Save as the "Pro" version
# model.save('beauty_model_pro.keras')
# print("PRO MODEL SAVED! Your accuracy should now be significantly higher.")





import tensorflow as tf
from tensorflow.keras import layers, models
import os

# ==========================================
# 1. SETTINGS
# ==========================================
data_dir = "images_datasets"
IMG_SIZE = (224, 224)
BATCH_SIZE = 32

# Data Loading
train_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)

# ==========================================
# 2. MODEL BUILDING (Transfer Learning)
# ==========================================
# MobileNetV2 Base
base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights='imagenet'
)
base_model.trainable = False 

# Full Model Architecture
model = models.Sequential([
    layers.Input(shape=(224, 224, 3)),
    
    # 1. Data Augmentation 
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.1),
    
    # 2. Preprocessing (MobileNetV2 specific)
    layers.Lambda(tf.keras.applications.mobilenet_v2.preprocess_input),
    
    # 3. Expert Brain
    base_model,
    
    # 4. Custom Layers for your 4 products
    layers.GlobalAveragePooling2D(),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.2),
    layers.Dense(4) # Output
])

model.compile(
    optimizer='adam',
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
    metrics=['accuracy']
)

# ==========================================
# 3. TRAINING
# ==========================================
print("🚀 Training starting...")
model.fit(train_ds, validation_data=val_ds, epochs=15)

# Save the model
model.save('beauty_model_final.keras')
print("✅ Done! 'beauty_model_final.keras' is ready.")