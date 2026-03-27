# import tensorflow as tf
# import os
# import imghdr

# # Configuration
# DATA_DIR = "images_datasets"

# def clean_and_validate_images():
#     print("--- Starting Data Cleaning Process ---")
#     image_exts = ['jpeg', 'jpg', 'bmp', 'png']
#     deleted_count = 0
#     valid_count = 0

#     if not os.path.exists(DATA_DIR):
#         print(f"Error: Folder '{DATA_DIR}' nahi mila!")
#         return

#     for category in os.listdir(DATA_DIR):
#         category_path = os.path.join(DATA_DIR, category)
#         if not os.path.isdir(category_path): 
#             continue
        
#         print(f"\nChecking category: {category}")
        
#         for image in os.listdir(category_path):
#             image_path = os.path.join(category_path, image)
#             try:
#                 # 1. Check extension authenticity
#                 tip = imghdr.what(image_path)
#                 if tip not in image_exts:
#                     print(f'-> REMOVING (Fake/Unsupported): {image}')
#                     os.remove(image_path)
#                     deleted_count += 1
#                     continue
                
#                 # 2. Check if TensorFlow can decode it
#                 img_content = tf.io.read_file(image_path)
#                 tf.image.decode_image(img_content)
#                 valid_count += 1
                
#             except Exception as e:
#                 print(f'-> REMOVING (Corrupt file): {image}')
#                 os.remove(image_path)
#                 deleted_count += 1

#     print("\n--- Cleaning Task Finished ---")
#     print(f"Total Valid Images: {valid_count}")
#     print(f"Total Deleted Images: {deleted_count}")

# if __name__ == "__main__":
#     clean_and_validate_images()


import tensorflow as tf
import os

# Configuration
DATA_DIR = "images_datasets"

def clean_and_validate_images():
    print("--- Starting Modern Data Cleaning Process ---")
    deleted_count = 0
    valid_count = 0

    if not os.path.exists(DATA_DIR):
        print(f"Error: Folder '{DATA_DIR}' not found!")
        return

    # Scanning categories (Lipstick, Powder, etc.)
    for category in os.listdir(DATA_DIR):
        category_path = os.path.join(DATA_DIR, category)
        if not os.path.isdir(category_path): 
            continue
        
        print(f"\nChecking category: {category}")
        
        for image in os.listdir(category_path):
            image_path = os.path.join(category_path, image)
            
            try:
                # STEP 1: Try to read the file
                img_content = tf.io.read_file(image_path)
                
                # STEP 2: Try to decode it as an image
                # If it's a fake JPG or corrupt, this line will trigger an error
                tf.image.decode_image(img_content)
                
                valid_count += 1
                
            except Exception as e:
                # If decoding fails, it's a "Fake" or "Corrupt" image
                print(f'-> REMOVING (Invalid Image): {image}')
                
                # Close the connection and remove the file
                if os.path.exists(image_path):
                    os.remove(image_path)
                deleted_count += 1

    print("\n--- Cleaning Task Finished ---")
    print(f"Total Valid Images: {valid_count}")
    print(f"Total Deleted Images: {deleted_count}")

if __name__ == "__main__":
    # To ignore the oneDNN warnings you saw in terminal
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 
    clean_and_validate_images()