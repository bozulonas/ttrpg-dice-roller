import os
import shutil

# --- Configuration ---
# Path to the source image you want to use as a placeholder
source_image_path = r'C:\Dice Chrome Extension\icons\d4_face1.png'

# The target directory where the dice face images should be stored
target_images_dir = './images/'

# Define the dice types and the number of faces they have
# d10 is handled slightly differently below to include face 10 (often represented as 0)
dice_config = {
    'd4': 4,
    'd6': 6,
    'd8': 8,
    'd10': 10, # We'll generate faces 1-10 for d10
    'd12': 12,
    'd20': 20
}

# --- Script Logic ---

# Ensure the source image exists
if not os.path.exists(source_image_path):
    print(f"Error: Source image not found at {source_image_path}")
    print("Please check the path and try again.")
    exit()

# Create the target directory if it doesn't exist
if not os.path.exists(target_images_dir):
    os.makedirs(target_images_dir)
    print(f"Created directory: {target_images_dir}")

print(f"Using '{source_image_path}' as the placeholder image.")
print("Creating placeholder files...")

# Iterate through each die type and face number
for die_type, num_faces in dice_config.items():
    print(f"Processing {die_type}...")
    # For d10, generate faces 1 through 10
    if die_type == 'd10':
         # Assuming faces are 1 to 10 (where 10 is often the '0' face)
         # If your images use 'd10_face0.png' for 10, adjust the range or rename later
         faces_to_generate = range(1, num_faces + 1)
    else:
        # For other dice, generate faces 1 through num_faces
        faces_to_generate = range(1, num_faces + 1)


    for face_number in faces_to_generate:
        # Construct the target file path
        target_file_name = f'{die_type}_face{face_number}.png'
        target_file_path = os.path.join(target_images_dir, target_file_name)

        try:
            # Copy the source image to the target path
            shutil.copy2(source_image_path, target_file_path)
            # print(f"  Created {target_file_path}") # Optional: uncomment for verbose output
        except IOError as e:
            print(f"  Error copying file {target_file_path}: {e}")
        except Exception as e:
            print(f"  An unexpected error occurred for {target_file_path}: {e}")

print("\nPlaceholder image creation complete.")
print(f"Check the '{target_images_dir}' directory.")
print("Remember to replace these placeholder images with actual dice face images later.")

