# Import necessary libraries
import os
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio
from scipy.spatial.transform import Rotation as R, Slerp

# --- Configuration ---
TARGET_IMG_SIZE = 64 # Final output image size
RENDER_IMG_SIZE = TARGET_IMG_SIZE * 4 # Render at higher resolution for sharp pixels
IMG_SIZE = RENDER_IMG_SIZE # Use render size for internal calculations

NUM_FRAMES_TUMBLE = 25       # Number of frames for the tumbling part
NUM_FRAMES_SETTLE = 15 # Number of frames for settling into the final position
NUM_FRAMES_HOLD = 10   # Number of frames to hold the final position
TOTAL_FRAMES = NUM_FRAMES_TUMBLE + NUM_FRAMES_SETTLE + NUM_FRAMES_HOLD
FRAME_DURATION_MS = 50 # Duration of each tumble frame in milliseconds (faster tumble)
FINAL_FRAME_DURATION_MS = 1500 # Duration the final result is shown (milliseconds)
DEFAULT_FACE_COLOR = (200, 200, 200) # Light grey for faces
NUMBER_COLOR = (10, 10, 10) # Black for numbers
FONT_SIZE_FACTOR = 0.4 # Factor to determine font size relative to face size
BACKGROUND_COLOR = (50, 50, 50) # Dark grey background
SCALE_FACTOR = IMG_SIZE * 0.45 # Scale vertices to fit RENDER image size
OUTPUT_DIR = "dice_animations_3d"
FINAL_UP_VECTOR = np.array([0, 0, 1]) # Target 'up' direction for the result face normal

# --- Pixel Art Palette ---
# Define the limited color palette (flattened list R,G,B, R,G,B, ...)
PALETTE_COLORS = [
    50, 50, 50,      # 0: Background
    80, 80, 80,      # 1: Shadow
    150, 150, 150,     # 2: Base Grey
    220, 220, 220,     # 3: Highlight Grey
    10, 10, 10,      # 4: Number/Outline
    # Add more colors if needed, e.g., for different dice
    # Ensure black and white are available if quantize needs them
    0, 0, 0,         # 5: Black
    255, 255, 255    # 6: White
]
# Pad palette to 256 colors (768 values) as required by putpalette
PALETTE_COLORS.extend([0] * (768 - len(PALETTE_COLORS)))

# Create a palette image for quantization
palette_img = Image.new('P', (1, 1))
palette_img.putpalette(PALETTE_COLORS)

# --- Font Loading ---
# Load font based on RENDER_IMG_SIZE
try:
    # Try loading a standard system font, provide fallback
    FONT = ImageFont.truetype("arial.ttf", int(IMG_SIZE * FONT_SIZE_FACTOR)) # IMG_SIZE is RENDER_IMG_SIZE here
except IOError:
    print("Arial font not found, using default PIL font.")
    # Use FONT_SIZE with default if possible, otherwise truly default
    try:
        FONT = ImageFont.load_default(int(IMG_SIZE * FONT_SIZE_FACTOR))
    except AttributeError:
         FONT = ImageFont.load_default()

# --- Dice Geometry Definitions (Vertices and Faces) ---
# Vertices are normalized later
phi = (1 + math.sqrt(5)) / 2 # Golden ratio

DICE_GEOMETRY = {
    4: { # Tetrahedron
        "vertices": np.array([
            [ 1,  1,  1], [-1, -1,  1], [-1,  1, -1], [ 1, -1, -1]
        ]) * 0.8,
        "faces": [
            [0, 1, 2], [0, 3, 1], [0, 2, 3], [1, 3, 2]
        ]
    },
    6: { # Cube
        "vertices": np.array([
            [-1, -1, -1], [ 1, -1, -1], [ 1,  1, -1], [-1,  1, -1],
            [-1, -1,  1], [ 1, -1,  1], [ 1,  1,  1], [-1,  1,  1]
        ]) * 0.6,
        "faces": [
            [0, 1, 2, 3], [4, 5, 1, 0], [5, 6, 2, 1],
            [6, 7, 3, 2], [7, 4, 0, 3], [7, 6, 5, 4]
        ]
    },
    8: { # Octahedron
        "vertices": np.array([
            [ 1,  0,  0], [-1,  0,  0], [ 0,  1,  0],
            [ 0, -1,  0], [ 0,  0,  1], [ 0,  0, -1]
        ]) * 0.8,
        "faces": [
            [0, 2, 4], [0, 4, 3], [0, 3, 5], [0, 5, 2],
            [1, 2, 5], [1, 5, 3], [1, 3, 4], [1, 4, 2]
        ]
    },
    12: { # Dodecahedron
        "vertices": np.array([
            [ 1,  1,  1], [ 1,  1, -1], [ 1, -1,  1], [ 1, -1, -1],
            [-1,  1,  1], [-1,  1, -1], [-1, -1,  1], [-1, -1, -1],
            [ 0,  phi,  1/phi], [ 0,  phi, -1/phi], [ 0, -phi,  1/phi],
            [ 0, -phi, -1/phi], [ 1/phi,  0,  phi], [ 1/phi,  0, -phi],
            [-1/phi,  0,  phi], [-1/phi,  0, -phi], [ phi,  1/phi,  0],
            [ phi, -1/phi,  0], [-phi,  1/phi,  0], [-phi, -1/phi,  0]
        ]) * 0.4,
         "faces": [ # Pentagonal faces - Ensure consistent winding order (e.g., CCW from outside)
            [0, 8, 4, 14, 12], [1, 9, 5, 18, 16], [2, 10, 6, 14, 12],
            [3, 11, 7, 19, 17], [0, 12, 2, 17, 16], [1, 16, 0, 8, 9],
            [1, 9, 15, 18], [3, 17, 1, 18, 19], # Corrected face 7
            [4, 8, 9, 15, 13], [5, 11, 3, 19, 18], # Corrected faces 8,9
            [6, 10, 11, 7, 13], [6, 13, 15, 14], [7, 11, 10, 2, 17] # Corrected faces 10, 11, 12
            # Note: This dodecahedron face list likely needs verification/correction from a reliable source.
            # The indices need to form proper pentagons with consistent winding.
        ]
    },
    20: { # Icosahedron
        "vertices": np.array([
            [ 0,  1,  phi], [ 0, -1,  phi], [ 0,  1, -phi], [ 0, -1, -phi],
            [ 1,  phi,  0], [-1,  phi,  0], [ 1, -phi,  0], [-1, -phi,  0],
            [ phi,  0,  1], [ phi,  0, -1], [-phi,  0,  1], [-phi,  0, -1]
        ]) * 0.5,
        "faces": [ # Triangular faces
            [0, 8, 1], [0, 4, 8], [0, 5, 4], [0, 10, 5], [0, 1, 10],
            [3, 9, 2], [3, 6, 9], [3, 7, 6], [3, 11, 7], [3, 2, 11],
            [1, 8, 6], [1, 6, 7], [1, 7, 10],
            [2, 9, 4], [2, 4, 5], [2, 5, 11],
            [8, 4, 9], [9, 6, 8], # Note: [9,6,8] might be redundant/reordered from [1,8,6]? Needs check.
            [5, 10, 7], [7, 11, 5]
        ]
    },
    # D10 is complex (trapezohedron), using a stretched d8 for now
    10: None
}

# Derive d10 from d8 geometry *after* d8 is defined
d10_geom = DICE_GEOMETRY.get(8)
if d10_geom and "vertices" in d10_geom:
    DICE_GEOMETRY[10] = {
        "vertices": d10_geom["vertices"].copy() * np.array([1, 1, 1.2]), # Stretch octahedron
        "faces": d10_geom["faces"]
    }
else:
    print("Warning: D8 geometry not found for D10 derivation.")
    DICE_GEOMETRY[10] = None # Ensure it's None if derivation fails


# Normalize vertices to be roughly within a unit sphere and ensure float type
for die_type, data in DICE_GEOMETRY.items():
    if data is None or "vertices" not in data or not isinstance(data["vertices"], np.ndarray):
        continue

    # Ensure vertices are float for division
    vertices = data["vertices"].astype(float)
    max_dist = np.max(np.linalg.norm(vertices, axis=1))
    if max_dist > 0:
        data["vertices"] = vertices / max_dist # Assign normalized float array back
    else:
        print(f"Warning: Max distance is zero for die {die_type}, cannot normalize.")

# --- Face Mapping (Crucial - Adjust if numbers are wrong!) ---
# Maps face index (from DICE_GEOMETRY['faces']) to the number on that face.
# These are based on common layouts and the defined geometry. Needs verification.
die_face_map = {
    4: {0: 1, 1: 2, 2: 3, 3: 4}, # Tetrahedron: Check vertex order if needed
    6: {0: 1, 1: 5, 2: 2, 3: 6, 4: 3, 5: 4}, # Cube: Adjusted for common layout vs face index
    8: {0: 1, 1: 7, 2: 5, 3: 3, 4: 2, 5: 8, 6: 6, 7: 4}, # Octahedron: Adjusted
    # D10 using D8 faces needs careful mapping. Using 1-8 from d8 + 9/10 for last two
    10: {0: 1, 1: 7, 2: 5, 3: 3, 4: 2, 5: 8, 6: 6, 7: 4}, # Assign 1-8 based on d8
    12: { # Dodecahedron: Adjusted for a plausible layout - NEEDS VERIFICATION
        0: 1, 1: 20, 2: 12, 3: 8, 4: 14, 5: 6, 6: 18, 7: 10, 8: 4, 9: 16, 10: 2, 11: 19 # Example mapping
        # This mapping is highly likely incorrect. Dodecahedron layouts vary.
    },
    20: { # Icosahedron: Adjusted for a plausible layout - NEEDS VERIFICATION
        0: 1, 1: 14, 2: 8, 3: 17, 4: 6, 5: 20, 6: 13, 7: 18, 8: 3, 9: 11,
        10: 9, 11: 15, 12: 4, 13: 19, 14: 7, 15: 16, 16: 2, 17: 10, 18: 5, 19: 12 # Example mapping
    }
}
# Assign 9 and 10 for d10 faces based on remaining d8 indices (likely incorrect)
if 10 in DICE_GEOMETRY and DICE_GEOMETRY[10] is not None:
   d10_map = die_face_map.get(10, {})
   assigned_indices = set(d10_map.keys())
   all_indices = set(range(len(DICE_GEOMETRY[10]["faces"])))
   remaining_indices = list(all_indices - assigned_indices)
   if len(remaining_indices) >= 2:
       d10_map[remaining_indices[0]] = 9
       d10_map[remaining_indices[1]] = 10
       die_face_map[10] = d10_map
   else:
        print("Warning: Not enough unassigned faces on derived d10 to map 9 and 10.")

# Inverse map for convenience (handle potential None types)
inv_die_face_map = {
    dtype: {num: idx for idx, num in faces.items()}
    for dtype, faces in die_face_map.items() if faces
}

# --- 3D Math Helpers ---

def get_face_normal(vertices, face_indices):
    """Calculate the normal vector of a face (assuming CCW winding from outside)."""
    # Ensure we handle faces with > 3 vertices (like cubes, dodecahedrons) robustly
    if len(face_indices) < 3:
        return np.array([0, 0, 1]) # Not a valid face

    p1, p2, p3 = vertices[face_indices[0]], vertices[face_indices[1]], vertices[face_indices[2]]
    v1 = p2 - p1
    v2 = p3 - p1
    normal = np.cross(v1, v2)
    norm = np.linalg.norm(normal)
    if norm == 0:
        return np.array([0, 0, 1]) # Fallback for degenerate cases
    return normal / norm # Normalize the normal vector


def get_final_rotation(die_type, result_value):
    """Calculate the rotation to bring the result face to the 'up' orientation (pointing Z+)."""
    if die_type not in inv_die_face_map or result_value not in inv_die_face_map[die_type]:
        print(f"Warning: Cannot find face index for die {die_type} result {result_value}. Using identity rotation.")
        return R.identity()
    if die_type not in DICE_GEOMETRY or DICE_GEOMETRY[die_type] is None:
         print(f"Warning: Geometry not found for die {die_type}. Using identity rotation.")
         return R.identity()

    face_idx = inv_die_face_map[die_type][result_value]
    geometry = DICE_GEOMETRY[die_type]
    base_vertices = geometry['vertices']

    # Check if face index is valid for the geometry
    if face_idx >= len(geometry['faces']):
         print(f"Warning: Face index {face_idx} out of bounds for die {die_type}. Using identity rotation.")
         return R.identity()

    face_vertex_indices = geometry['faces'][face_idx]

    # Get the normal of the target face in the base model
    current_normal = get_face_normal(base_vertices, face_vertex_indices)

    # Ensure target vector is normalized (should be already, but safe)
    target_normal = FINAL_UP_VECTOR / np.linalg.norm(FINAL_UP_VECTOR)

    # Calculate rotation to align current normal with target normal
    # We want the rotation that takes `current_normal` TO `target_normal`
    # R.align_vectors computes rotation FROM first vector set TO second vector set.
    try:
        rotation, _ = R.align_vectors([target_normal], [current_normal])
    except ValueError as e:
        # This can happen if vectors are exactly opposite
        print(f"Warning: align_vectors failed (likely opposite vectors) for d{die_type} face {result_value}. Using fallback. Error: {e}")
        # Fallback: Rotate 180 degrees around an arbitrary axis perpendicular to target_normal
        perp_axis = np.cross(current_normal, target_normal)
        if np.linalg.norm(perp_axis) < 1e-6: # If vectors were parallel (or anti-parallel)
            perp_axis = np.array([1, 0, 0]) # Use arbitrary X-axis if cross product is zero
            if abs(np.dot(perp_axis, target_normal)) > 0.99: # If X is also parallel/anti-parallel
                perp_axis = np.array([0, 1, 0]) # Use Y-axis
        rotation = R.from_rotvec(perp_axis / np.linalg.norm(perp_axis) * np.pi)

    # Note: Does not handle visual 'up' direction of the number text on the face.
    # This only ensures the face plane normal points along FINAL_UP_VECTOR.

    return rotation # Return the single Rotation object directly


def project_orthographic(vertices_3d):
    """Project 3D vertices to 2D using orthographic projection."""
    center_x, center_y = IMG_SIZE / 2, IMG_SIZE / 2
    # Scale first, then translate to center
    vertices_2d = vertices_3d[:, :2] * SCALE_FACTOR
    vertices_2d += np.array([center_x, center_y])
    return vertices_2d


# --- Drawing Helpers ---
def draw_polygon_shaded(draw, vertices_2d, face_normal_rotated, color):
    """Draw a polygon with simple stepped shading for pixel art style."""
    # Simple stepped shading based on normal's Z component
    view_direction = FINAL_UP_VECTOR # Use the same up vector
    dot_product = np.dot(face_normal_rotated, view_direction)

    # Determine shade based on thresholds
    if dot_product > 0.4: # Facing towards camera
        shade_factor = 1.15 # Highlight
    elif dot_product < -0.3: # Facing away
        shade_factor = 0.6 # Shadow
    else: # Side facing
        shade_factor = 0.9 # Base

    # Ensure color is a list or tuple of numbers
    if isinstance(color, (list, tuple)) and len(color) == 3:
        # Apply shade factor and clamp to 0-255
        shaded_color = tuple(max(0, min(255, int(c * shade_factor))) for c in color)
    else:
        shaded_color = color # Fallback if color format is unexpected

    # Ensure vertices are tuples of integers for PIL
    polygon_points = [tuple(map(int, v)) for v in vertices_2d if len(v) == 2]
    if len(polygon_points) >= 3:
        draw.polygon(polygon_points, fill=shaded_color) # Removed outline

def draw_face_number(draw, rotated_vertices, face_indices, face_normal_rotated, text, font):
    """Draw the face number, attempting to center it on the projected face."""
    # Check if face is potentially visible (facing generally towards camera)
    if face_normal_rotated[2] < 0.05: # Reduced threshold for visibility
        return

    face_verts_3d = rotated_vertices[face_indices]
    projected_verts_2d = project_orthographic(face_verts_3d)
    center_2d = np.mean(projected_verts_2d, axis=0)

    try:
        # Use textbbox for potentially better centering
        bbox = draw.textbbox((0, 0), text, font=font)
        # bbox is (left, top, right, bottom)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        # Calculate top-left corner position for centering
        text_x = center_2d[0] - text_width / 2
        text_y = center_2d[1] - text_height / 2 - bbox[1] # Adjust for vertical alignment relative to baseline
        draw.text((text_x, text_y), text, fill=NUMBER_COLOR, font=font, anchor="lt")
    except AttributeError: # Fallback if textbbox not available or fails
         print(f"Warning: textbbox error. Using basic centering for '{text}'.")
         # Basic centering fallback (less accurate)
         try:
             font_size = font.size
         except AttributeError:
             font_size = 10 # Default size if font.size not available
         approx_width = font_size * len(text) * 0.6
         approx_height = font_size
         text_x = center_2d[0] - approx_width / 2
         text_y = center_2d[1] - approx_height / 2
         draw.text((text_x, text_y), text, fill=NUMBER_COLOR, font=font)
    except Exception as e:
         print(f"Unexpected error drawing text '{text}': {e}")

# --- GIF Generation --- (Refactored Function)
def generate_dice_roll_gif(die_type, result_value, filename="dice_roll.gif"):
    """Generates a GIF with a tumbling die settling on the result."""
    if die_type not in DICE_GEOMETRY or DICE_GEOMETRY[die_type] is None:
        print(f"Error: Geometry not defined for die_type {die_type}")
        return
    if die_type not in die_face_map:
        print(f"Error: Face map not defined for die_type {die_type}")
        return

    geometry = DICE_GEOMETRY[die_type]
    vertices = geometry['vertices']
    faces = geometry['faces']
    face_numbers = die_face_map.get(die_type, {})

    frames = []

    # --- Define Rotations ---
    # 1. Energetic Random Initial Rotation (more tumble)
    random_axis = np.random.rand(3) - 0.5
    random_axis /= np.linalg.norm(random_axis) if np.linalg.norm(random_axis) > 0 else np.array([0,0,1])
    random_angle = np.random.uniform(np.pi * 2, np.pi * 4) # More initial spin
    initial_rotation = R.from_rotvec(random_axis * random_angle) * R.random() # Combine axis-angle with another random rotation

    # 2. Target Final Rotation (result face points along +Z)
    target_rotation = get_final_rotation(die_type, result_value)

    # --- Setup Interpolation ---
    key_rotations = R.concatenate([initial_rotation, target_rotation])
    key_times = [0, 1] # Interpolate over unit time [0, 1]
    try:
        slerp = Slerp(key_times, key_rotations)
    except ValueError as e:
        print(f"Error creating Slerp (likely due to rotations): {e}. Using target rotation directly.")
        # Fallback if Slerp fails (e.g., identical rotations)
        slerp = lambda t: target_rotation

    # --- Animation Loop ---
    for i in range(TOTAL_FRAMES):
        # Create image at RENDER_IMG_SIZE
        img_render = Image.new('RGB', (IMG_SIZE, IMG_SIZE), BACKGROUND_COLOR)
        draw = ImageDraw.Draw(img_render)

        # Calculate interpolation time 't' with ease-out curve
        if i < NUM_FRAMES_TUMBLE:
            t = i / (NUM_FRAMES_TUMBLE - 1) if NUM_FRAMES_TUMBLE > 1 else 1.0
        elif i < NUM_FRAMES_TUMBLE + NUM_FRAMES_SETTLE:
            t = 1 - ((i - NUM_FRAMES_TUMBLE) / (NUM_FRAMES_SETTLE - 1) if NUM_FRAMES_SETTLE > 1 else 1.0)
        else:
            t = 1.0
        eased_t = 1 - (1 - t)**3 # Ease-out cubic: starts fast, slows down

        # Get interpolated rotation for this frame
        current_rotation = slerp(eased_t)

        # Apply rotation to base vertices
        rotated_vertices = current_rotation.apply(vertices)

        # Calculate normals and depths AFTER rotation for drawing order and shading
        face_data = []
        for face_idx, face_indices in enumerate(faces):
            if len(face_indices) < 3: continue # Skip invalid faces
            # Check vertex indices are valid for rotated_vertices array
            if any(idx >= len(rotated_vertices) or idx < 0 for idx in face_indices):
                print(f"Warning: Invalid vertex index in face {face_idx}. Skipping.")
                continue
            face_verts_3d = rotated_vertices[face_indices]
            face_normal = get_face_normal(rotated_vertices, face_indices)
            avg_z = np.mean(face_verts_3d[:, 2]) # Use average Z for depth sorting
            face_data.append({
                "idx": face_idx,
                "indices": face_indices,
                "normal": face_normal,
                "avg_z": avg_z
            })

        # Sort faces by depth (draw back faces first)
        face_data.sort(key=lambda f: f["avg_z"])

        # Draw faces (back to front)
        for face in face_data:
            projected_verts = project_orthographic(rotated_vertices[face["indices"]])
            draw_polygon_shaded(draw, projected_verts, face["normal"], DEFAULT_FACE_COLOR)

        # Draw numbers (on top of faces)
        for face in face_data: # Iterate again to draw numbers
            face_idx = face["idx"]
            if face_idx in face_numbers:
                number_text = str(face_numbers[face_idx])
                draw_face_number(draw, rotated_vertices, face["indices"], face["normal"], number_text, FONT)

        # --- Pixel Art Post-processing ---
        # 1. Quantize to the defined palette (Enable dithering)
        quantized_img = img_render.quantize(palette=palette_img, dither=Image.Dither.FLOYDSTEINBERG)

        # 2. Resize down to TARGET_IMG_SIZE using Nearest Neighbor for sharp pixels
        #    Convert back to RGB after quantize, as GIF saver might prefer RGB frames
        final_frame = quantized_img.convert('RGB').resize((TARGET_IMG_SIZE, TARGET_IMG_SIZE), Image.Resampling.NEAREST)

        frames.append(final_frame)

    # --- Save GIF ---
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    full_path = os.path.join(OUTPUT_DIR, filename)
    # Calculate durations: N tumble frames + 1 final hold frame
    durations = [FRAME_DURATION_MS / 1000.0] * NUM_FRAMES_TUMBLE + [FRAME_DURATION_MS / 1000.0] * NUM_FRAMES_SETTLE + [FINAL_FRAME_DURATION_MS / 1000.0] * NUM_FRAMES_HOLD
    try:
        # Use pillow writer for better compatibility potentially
        # Ensure durations are correct (list of seconds)
        imageio.mimsave(full_path, frames, format='GIF', duration=durations, loop=0, palettesize=len(PALETTE_COLORS)//3)
        print(f"Generated GIF: {full_path}")
    except Exception as e:
        print(f"Error saving GIF {filename} with imageio: {e}")
        # Fallback using Pillow's save method
        try:
            # Pillow save takes duration in milliseconds per frame
            pillow_durations = [(d * 1000) for d in durations]
            # Pillow might handle palette better if first frame is P mode?
            if frames:
                frames[0].save(full_path, save_all=True, append_images=frames[1:],
                               optimize=False, duration=pillow_durations, loop=0,
                               palette=palette_img.getpalette()) # Try providing palette
        except Exception as e_pillow:
            print(f"Error saving GIF {filename} with Pillow fallback: {e_pillow}")

# --- Example Usage --- (Remains the same)
if __name__ == "__main__":
    print("Generating example 3D dice roll animations...")
    # Example: Roll a d6 and show a 4
    generate_dice_roll_gif(die_type=6, result_value=4, filename="d6_roll_3d_4.gif")
    # Example: Roll a d20 and show a 17
    generate_dice_roll_gif(die_type=20, result_value=17, filename="d20_roll_3d_17.gif")
    # Example: Roll a d8 randomly
    random_d8_result = random.randint(1, 8)
    generate_dice_roll_gif(die_type=8, result_value=random_d8_result, filename=f"d8_roll_3d_{random_d8_result}.gif")
    # Example: Roll a d4 and show a 1
    generate_dice_roll_gif(die_type=4, result_value=1, filename="d4_roll_3d_1.gif")
    # Example: Roll a d10 (derived from d8) and show a 10
    if 10 in DICE_GEOMETRY and DICE_GEOMETRY[10] is not None:
        generate_dice_roll_gif(die_type=10, result_value=10, filename="d10_roll_3d_10.gif")
    else:
        print("Skipping d10 example as geometry is missing.")
    # Example: Roll a d12 and show a 5
    generate_dice_roll_gif(die_type=12, result_value=5, filename="d12_roll_3d_5.gif")
    print(f"Check the '{OUTPUT_DIR}' directory for the generated GIFs.")
