import os
import shutil
import re

# --- Configuration ---
# The folder where the original cropped dice images are located
source_folder = 'cropped_grid_dice'
# The new folder where the renumbered d10 images will be saved
target_folder = 'd10_renumbered'
# The name of the manual file to include, located in the script's root directory
manual_file_name = 'manual d10_face10.png'
# The desired name for the manual file in the target folder
manual_file_target_name = 'd10_face10.png'

# --- Script Logic ---

# Create the target folder if it doesn't exist
if not os.path.exists(target_folder):
    os.makedirs(target_folder)
    print(f"Created target folder: {target_folder}")

# Check if the source folder exists
if not os.path.exists(source_folder):
    print(f"Error: Source folder '{source_folder}' not found.")
    print("Please ensure the 'cropped_grid_dice' folder exists and contains the d10 images.")
else:
    # List all files in the source folder
    all_files = os.listdir(source_folder)

    # Filter for d10 face images, excluding d10_face1.png
    # Use a regex to match files like 'd10_faceN.png' where N is a digit, and N > 1
    d10_files_to_process = []
    # Regex to find 'd10_face' followed by one or more digits, ending with '.png'
    d10_pattern = re.compile(r'^d10_face(\d+)\.png$', re.IGNORECASE)

    for filename in all_files:
        match = d10_pattern.match(filename)
        if match:
            face_number = int(match.group(1))
            # Include files where the face number is greater than 1
            if face_number > 1:
                d10_files_to_process.append((filename, face_number))

    # Sort the list of files based on the original face number
    # This ensures that face2 comes before face3, etc., for correct renumbering
    d10_files_to_process.sort(key=lambda item: item[1])

    print(f"Found {len(d10_files_to_process)} d10 files (excluding d10_face1.png) to renumber.")

    # Copy and renumber the selected d10 files
    for index, (original_filename, original_face_number) in enumerate(d10_files_to_process):
        # Calculate the new face number (original number - 1)
        new_face_number = original_face_number - 1

        # Construct the new filename
        new_filename = f"d10_face{new_face_number}.png"

        # Construct the full source and destination paths
        source_path = os.path.join(source_folder, original_filename)
        target_path = os.path.join(target_folder, new_filename)

        # Copy the file (using copy2 to preserve metadata like modification times)
        shutil.copy2(source_path, target_path)
        print(f"Copied and renamed: {original_filename} -> {new_filename}")

    # --- Handle the manual file ---
    manual_source_path = manual_file_name
    manual_target_path = os.path.join(target_folder, manual_file_target_name)

    # Check if the manual file exists in the root directory
    if os.path.exists(manual_source_path):
        # Copy the manual file to the target folder with the desired name
        shutil.copy2(manual_source_path, manual_target_path)
        print(f"\nCopied manual file: {manual_file_name} -> {manual_file_target_name}")
    else:
        print(f"\nWarning: Manual file '{manual_file_name}' not found in the script's directory.")
        print(f"Please place '{manual_file_name}' in the same folder as the script if you want it included.")

    print("\nScript finished.")
    print(f"Check the '{target_folder}' folder for the renumbered d10 images and the manual file.")