import tensorflow as tf
from tensorflow.keras import layers
import matplotlib.pyplot as plt

# 1. Setup paths and constants
data_dir = "images_datasets"
IMG_SIZE = (224, 224) 
BATCH_SIZE = 32

# 2. Load the dataset
print("--- Loading images from folders ---")
train_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)

# 3. FIX: Save the class names BEFORE normalization
class_names = train_ds.class_names
print(f"✅ Found classes: {class_names}")

# 4. Normalization (Math Scaling)
normalization_layer = layers.Rescaling(1./255)
train_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))

# 5. Define Augmentation (The Data Multiplier)
data_augmentation = tf.keras.Sequential([
  layers.RandomFlip("horizontal"),
  layers.RandomRotation(0.2),
  layers.RandomZoom(0.1),
])

# 6. Visual Proof (Updated to show DIFFERENT products)
plt.figure(figsize=(10, 10))
for images, labels in train_ds.take(1):
    for i in range(9):
        # We apply augmentation to the "i-th" image in the batch
        augmented_images = data_augmentation(images)
        ax = plt.subplot(3, 3, i + 1)
        
        # CHANGE: Use [i] instead of [0] to see different products
        plt.imshow(augmented_images[i].numpy()) 
        
        # CHANGE: Use labels[i] to get the correct name for each specific image
        plt.title(f"Label: {class_names[labels[i]]}")
        plt.axis("off")

print("--- Opening mixed visualization window... ---")
plt.show()