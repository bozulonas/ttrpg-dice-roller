import cv2
import os

# Define the input image file. Make sure this file is in the same directory as the script,
# or provide the full path to the image file.
image_path = 'All Dice Faces.jpg'

# Define the output folder where the cropped images will be saved.
output_folder = 'cropped_grid_dice'

# Create the output folder if it doesn't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    print(f"Created output folder: {output_folder}")

# Load the image
img = cv2.imread(image_path)

# Check if the image was loaded successfully
if img is None:
    print(f"Error: Could not load image from {image_path}")
    print("Please ensure the image file exists and the path is correct.")
else:
    print(f"Image loaded successfully from {image_path}")

    # Define the bounding boxes for the groups of dice faces and their grid layout.
    # Format: 'dice_type': ((bbox_x1, bbox_y1, bbox_x2, bbox_y2), (grid_cols, grid_rows))
    # where (bbox_x1, bbox_y1) is the top-left corner and (bbox_x2, bbox_y2) is the
    # bottom-right corner of the bounding box containing all the faces for that dice type.
    # (grid_cols, grid_rows) define how many columns and rows of dice faces are within that bbox.
    #
    # These coordinates and grid sizes are based on visual inspection of image_941aa1.jpg
    # and your description of the grid layouts and total counts.
    # **You will likely need to adjust these bounding box coordinates** to precisely
    # match the groups of dice in your image for perfect cropping.
    dice_info = {
        'd20': ((42, 190, 353, 457), (5, 4)), # Bbox (x1,y1,x2,y2), Grid (cols, rows)
        'd12': ((373, 192, 618, 373), (4, 3)),
        'd10': ((630, 191, 959, 320), (5, 2)),
        'd8': ((367, 397, 623, 525), (4, 2)),
        # For d4 and d6, assuming the user meant the first row of faces in their respective blocks.
        # If you need more than the first row, you'll need to adjust the bbox_y2 and grid_rows.
        'd4': ((74, 465, 330, 524), (4, 1)), # Bbox for the first row of d4s, 4 columns, 1 row
        'd6': ((638, 476, 951, 525), (6, 1)),# Bbox for the first row of d6s, 6 columns, 1 row
    }

    # Iterate through the dice types and their information
    for dice_type, (bbox, grid) in dice_info.items():
        bbox_x1, bbox_y1, bbox_x2, bbox_y2 = bbox
        grid_cols, grid_rows = grid

        # Calculate the width and height of each individual cell (dice face) within the grid
        # Use float division first for accuracy, then convert to int for coordinates
        cell_width_float = (bbox_x2 - bbox_x1) / grid_cols
        cell_height_float = (bbox_y2 - bbox_y1) / grid_rows

        # Ensure cell dimensions are positive
        if cell_width_float <= 0 or cell_height_float <= 0:
             print(f"Warning: Invalid bounding box or grid dimensions for {dice_type}. Skipping.")
             continue

        print(f"Processing {dice_type} with grid {grid_cols}x{grid_rows} in bbox ({bbox_x1},{bbox_y1},{bbox_x2},{bbox_y2}). Estimated cell size {cell_width_float:.2f}x{cell_height_float:.2f}")

        face_index = 1
        # Iterate through the grid rows and columns to crop each face
        for row in range(grid_rows):
            for col in range(grid_cols):
                # Calculate the coordinates for the current face's bounding box
                x1 = int(bbox_x1 + col * cell_width_float)
                y1 = int(bbox_y1 + row * cell_height_float)
                x2 = int(bbox_x1 + (col + 1) * cell_width_float)
                y2 = int(bbox_y1 + (row + 1) * cell_height_float)

                # Ensure calculated coordinates are within the main image bounds (safety check)
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(img.shape[1], x2)
                y2 = min(img.shape[0], y2)

                # Check if the calculated coordinates define a valid region to crop
                if x2 > x1 and y2 > y1:
                    # Crop the image using NumPy slicing (OpenCV images are NumPy arrays)
                    cropped_img = img[y1:y2, x1:x2]

                    # Define the output filename with dice type and index
                    output_filename = os.path.join(output_folder, f"{dice_type}_face{face_index}.png")

                    # Save the cropped image
                    cv2.imwrite(output_filename, cropped_img)
                    # print(f"Saved {output_filename}") # Optional: uncomment for detailed progress

                    face_index += 1
                else:
                    print(f"Warning: Invalid calculated crop coordinates for {dice_type} face {face_index}: ({x1}, {y1}, {x2}, {y2}). Skipping.")

    print("\nProcessing complete. Please check the 'cropped_grid_dice' folder.")
    print("Review the saved images. If the cropping is not accurate for any dice type,")
    print("edit the corresponding bounding box coordinates (bbox_x1, bbox_y1, bbox_x2, bbox_y2)")
    print("or grid dimensions (grid_cols, grid_rows) in the 'dice_info' dictionary in the script and run it again.")
    print("Minor adjustments to the bbox coordinates are usually needed for perfect alignment.")