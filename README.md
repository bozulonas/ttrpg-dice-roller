# TTRPG Dice Roller Chrome Extension

A simple and intuitive Chrome Extension for rolling dice for tabletop roleplaying games directly from your browser toolbar.

## Features

- **Quick Access**: Roll dice directly from a pop-up window activated by a browser toolbar icon.
- **Polyhedral Dice Support**: Includes standard TTRPG dice types (d4, d6, d8, d10, d12, d20).
- **Visual Dice Tray**: Select dice by clicking icons, and see them appear visually in a "rolling area" before you roll.
- **Click to Remove**: Easily remove selected dice from the rolling area by clicking on their icons.
- **Dynamic Roll Button**: The main button updates to show the current dice selection (e.g., "Roll: 3d6 + 1d20").
- **Roll Animation & Sound**: Dice visually tumble with a pleasing falloff animation and sound effect when rolled.
- **Re-roll Individual Dice**: Click on a rolled die image to re-roll just that single die with animation and sound, and update the total sum.
- **"Roll Again" Functionality**: Click the main button when no new dice are selected to re-roll the exact same pool as the last roll.
- **Instant Roll (Ctrl+Click)**: Hold Ctrl and click a dice selection icon to instantly roll 1 of that die type, bypassing the selection area.

## Installation

1. Download or clone this repository to your local machine.
2. Open Google Chrome.
3. Navigate to `chrome://extensions/`.
4. Enable "Developer mode" using the toggle switch in the top right corner.
5. Click the "Load unpacked" button in the top left corner.
6. Select the folder where you downloaded/cloned the extension files (ttrpg-dice-roller).
7. The extension should now appear in your list of installed extensions, and its icon (a die) should be visible in your Chrome toolbar.

## Usage

1. Click the Dice Icon in your Chrome toolbar to open the pop-up.
2. The pop-up displays a row of standard dice icons (d4, d6, d8, d10, d12, d20). These icons show their maximum face value by default.

### Select Dice
- Left-click one of the dice icons in the selection row to add one of that die type to your rolling area (the dashed box below the selection row).
- Right-click one of the dice icons in the selection row to remove the last added die of that type from your rolling area.
- As you add/remove dice, the text on the main "Roll" button at the top will update to show your current selection (e.g., "Roll: 2d6 + 1d20").

### Remove Selected Dice
- Click on any die icon that you have added to the rolling area (the icons in the dashed box) to remove it from your current selection.

### Perform Roll
1. Click the "Roll: XdY" button at the top.
   - If you have dice currently in the rolling area, these dice will be rolled. The rolling area will clear, and the animation will begin.
   - If the rolling area is empty, the button will show "Roll Again: XdY" (based on your last roll). Clicking it will re-roll the previous dice pool.
2. Rolling Animation: The selected dice will animate in the results area, cycling through faces with a sound effect.
3. View Results: After the animation finishes, the dice will settle on their final rolled faces, and the total sum will be displayed below them.

### Additional Features
- **Re-roll Single Die**: Click on any of the dice images after they have been rolled to re-roll just that specific die. It will animate and update the total sum.
- **Instant Roll (Ctrl+Click)**: Hold down the Ctrl key and Left-click one of the original dice icons in the selection row (the top row). This will immediately roll 1 of that die type without adding it to the selection area.

## File Structure

```
ttrpg-dice-roller/
├── manifest.json       # Extension manifest file (name, version, permissions, popup)
├── popup/              # Contains files for the pop-up window
│   ├── popup.html      # Structure of the pop-up UI
│   ├── popup.css       # Styling for the pop-up
│   └── popup.js        # JavaScript logic for dice selection, rolling, animation, etc.
├── icons/              # Extension icon files
│   ├── dice16.png      # 16x16 icon
│   ├── dice48.png      # 48x48 icon
│   └── dice128.png     # 128x128 icon
├── images/             # Dice face image assets
│   ├── d4_face1.png    # Image for d4 showing face 1
│   ├── ...             # Images for all faces of all dice types (d4, d6, d8, d10, d12, d20)
│   └── d20_face20.png
└── audio/              # Audio assets
    └── roll_sound.mp3  # Sound file for the rolling effect (replace with your own if needed)
## Assets

This extension requires image files for each face of each die type (d4, d6, d8, d10, d12, d20) and a sound file for the rolling effect. Placeholder images can be generated using the provided Python script if needed.

- Ensure your image files are named consistently (e.g., `d6_face1.png`, `d6_face2.png`, ..., `d6_face6.png`) and placed in the `images/` directory.
- The d10 face representing '10' should ideally be named `d10_face10.png`, but the code includes comments for adjusting if you use `d10_face0.png`.

## Contributing

Contributions are welcome! If you find a bug or have an idea for a new feature, please open an issue or submit a pull request.

## License

MIT License

Copyright (c) 2025 

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.