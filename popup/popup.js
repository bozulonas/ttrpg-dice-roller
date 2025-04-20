// --- State ---
// This state will track the number of each die type currently displayed in the resultsArea
// before a roll. It is updated directly by handleDiceClick and the removeSelectedDie listener.
let selectedDice = { d4: 0, d6: 0, d8: 0, d10: 0, d12: 0, d20: 0 };
// Store the configuration of the last roll {d4: N, d6: M, ...}
let lastRollsConfig = {};
// Store the actual results of the last roll [{type: 'd6', result: 4}, ...]
// This array will be updated when individual dice are re-rolled.
let lastRollResults = [];


// --- DOM Elements ---
const rollBtn = document.getElementById('rollBtn'); // Now the main button at the top
const diceSelector = document.querySelector('.dice-selector'); // The container for original dice icons
const originalDiceIcons = document.querySelectorAll('.dice-selector .dice-icon.original'); // The initial icons
const resultsArea = document.getElementById('resultsArea'); // This area now shows selected dice AND rolling animation

// --- Audio ---
// Assuming this path is correct for your sound file
const rollSound = new Audio('../audio/560085__vartian__rolling-single-and-dual-20-sided-dice_trimmed_1.1.wav');

// --- Functions ---

// Update the Roll button text and state
// This now directly uses the selectedDice state, which is updated by handleDiceClick and removeSelectedDie.
function updateRollButtonDisplay() {
    let notation = [];
    let totalDice = 0;
    for (const type in selectedDice) {
        if (selectedDice[type] > 0) {
            notation.push(`${selectedDice[type]}${type}`);
            totalDice += selectedDice[type];
        }
    }

    if (totalDice > 0) {
        rollBtn.textContent = `Roll: ${notation.join(' + ')}`;
        rollBtn.disabled = false;
    } else if (Object.keys(lastRollsConfig).length > 0) {
        // If no dice currently selected (selectedDice is empty), but there was a last roll config
        let lastNotation = [];
        for (const type in lastRollsConfig) {
             if (lastRollsConfig[type] > 0) {
                 // FIX: Access count from lastRollsConfig, not lastNotation array
                 lastNotation.push(`${lastRollsConfig[type]}${type}`);
             }
        }
         rollBtn.textContent = `Roll Again: ${lastNotation.join(' + ')}`;
         rollBtn.disabled = false; // Can roll again even if 0 currently selected
    }
    else {
        rollBtn.textContent = 'Roll: Select dice below';
        rollBtn.disabled = true;
    }
}

// Get random face image path for a die type
function getRandomFaceImage(dieType) {
    const maxFaces = parseInt(dieType.substring(1));
    const randomFace = Math.floor(Math.random() * maxFaces) + 1;
     // Handle d10 face 10 (often represented as 0) - assuming face 10 image is named _face10.png
     if (dieType === 'd10' && maxFaces === 10 && randomFace === 10) {
         return `../images/${dieType}_face10.png`;
     }
      // Handle d10 face 0 if it represents 10 and your images are named _face0.png
     if (dieType === 'd10' && maxFaces === 10 && randomFace === 10 && false /* set to true if d10 face 10 is named _face0.png */) {
          return `../images/${dieType}_face0.png`;
     }
    return `../images/${dieType}_face${randomFace}.png`;
}

// Roll a single die
function rollDie(dieType) {
  const maxFaces = parseInt(dieType.substring(1));
  return Math.floor(Math.random() * maxFaces) + 1;
}

// Handle clicks on selected dice icons in the resultsArea to remove them BEFORE a roll
function removeSelectedDie(event) {
    const clickedDieElement = event.currentTarget;
    const dieType = clickedDieElement.dataset.die;

    // Ensure this is a pre-roll selected die icon
    if (!clickedDieElement.classList.contains('selected-die-icon')) {
        return;
    }

    if (selectedDice[dieType] > 0) {
        clickedDieElement.remove(); // Remove the clicked element from the DOM
        selectedDice[dieType]--; // Decrement state count
        lastRollsConfig = {}; // Reset lastRollsConfig as selection changed
        updateRollButtonDisplay(); // Update button text and state
    }
    // If count is already 0 (shouldn't happen if UI is in sync), do nothing
}


// Handle dice icon clicks (left and right) on the original icons in the selector
function handleDiceClick(event) {
  const clickedIcon = event.currentTarget;
  // Ensure we only process clicks on the original icons in the selector area
  if (!clickedIcon.classList.contains('original')) {
      return; // Ignore clicks on duplicates (though there shouldn't be any here now)
  }

  const dieType = clickedIcon.dataset.die;
  const isRightClick = event.button === 2; // 0 for left, 2 for right

  event.preventDefault(); // Prevent context menu on right-click

  if (isRightClick) {
      // --- NEW: Perform instant roll on right-click ---
      performInstantRoll(dieType);
      // ----------------------------------------------
  } else { // Left click
      // Add a visual representation of the selected die to the resultsArea
      const selectedDieElement = document.createElement('img');
      selectedDieElement.classList.add('selected-die-icon'); // Use a new class for pre-roll icons
      selectedDieElement.dataset.die = dieType; // Store die type
      // Use the max face image as the default visual representation before rolling
      const maxFace = parseInt(dieType.substring(1));
      let defaultFace = maxFace;
      // Adjust for d10 if max face 10 is represented by face 10 image
       if (dieType === 'd10' && maxFace === 10) {
           defaultFace = 10; // Use 10 if your image is d10_face10.png
       }
       // Adjust for d10 if max face 10 is represented by face 0 image
       if (dieType === 'd10' && maxFace === 10 && false /* set to true if d10 max face is named _face0.png */) {
            defaultFace = 0; // Use 0 if your image is d10_face0.png
       }

      selectedDieElement.src = `../images/${dieType}_face${defaultFace}.png`;
      selectedDieElement.alt = dieType;

      // Add the click listener to the newly created selected die icon for removal
      selectedDieElement.addEventListener('click', removeSelectedDie);

      resultsArea.appendChild(selectedDieElement); // Add it to the results area

      selectedDice[dieType]++; // Increment state count

      // Reset lastRollsConfig because the user is making a new selection
      lastRollsConfig = {};
      updateRollButtonDisplay(); // Update button text and state after modifying selection
  }

  // Note: updateRollButtonDisplay is now called only within the left-click logic
  // or at the end of performInstantRoll for right-clicks.
}


// --- NEW Function: Perform Instant Roll ---
function performInstantRoll(dieType) {
    console.log(`Performing instant roll for: ${dieType}`);
    // 1. Clear results area
    resultsArea.innerHTML = '';

    // 2. Play sound
    rollSound.currentTime = 0;
    rollSound.play().catch(e => console.error("Sound playback failed:", e));

    // 3. Roll the die
    const finalResult = rollDie(dieType);

    // 4. Create and add the die element
    const dieElement = document.createElement('img');
    dieElement.classList.add('rolled-die'); // Use rolled-die class
    dieElement.dataset.die = dieType;
    dieElement.dataset.index = 0; // Only one die, index is 0
    dieElement.src = getRandomFaceImage(dieType); // Start with random face
    dieElement.alt = dieType;
    resultsArea.appendChild(dieElement);

    // 5. Animation Logic (adapted from rerollSingleDie)
    let intervalTime = 50;
    const intervalIncrease = 15;
    const maxIntervalTime = 300;
    const minDuration = 250;
    const maxDuration = 800; // Slightly shorter max for single instant roll? User preference.
    const animationDuration = Math.floor(Math.random() * (maxDuration - minDuration + 1)) + minDuration;
    let startTime = Date.now();

    function animateInstant() {
        const elapsed = Date.now() - startTime;

        if (elapsed < animationDuration) {
            // Still animating
            dieElement.src = getRandomFaceImage(dieType);
            const progress = elapsed / animationDuration;
            let currentInterval = intervalTime + progress * (maxIntervalTime - intervalTime);
            currentInterval = Math.min(currentInterval, maxIntervalTime);
            setTimeout(animateInstant, currentInterval);
        } else {
            // Animation finished
            let faceToShow = finalResult;
             if (dieType === 'd10' && finalResult === 10) {
                 faceToShow = 10;
             } else if (dieType === 'd10' && finalResult === 0) { // If rollDie can return 0
                 faceToShow = 10;
             }
            dieElement.src = `../images/${dieType}_face${faceToShow}.png`;

            // 6. Update state AFTER animation
            lastRollResults = [{ type: dieType, result: finalResult }]; // Set result for this single roll
            // Reset lastRollsConfig to reflect this instant roll as the "last roll"
            lastRollsConfig = {}; // Clear any previous multi-die config
            lastRollsConfig[dieType] = 1; // Set config for this single die

            // 7. Display sum and update button
            displayTotalSum();
            updateRollButtonDisplay(); // Update button to show "Roll Again: 1dX"

            // 8. Add re-roll listener (optional for instant roll, but consistent)
            dieElement.addEventListener('click', rerollSingleDie);
             dieElement.style.pointerEvents = 'auto'; // Ensure clickable if needed
        }
    }

    animateInstant(); // Start animation
}
// --- End NEW Function ---


// Handle clicks on rolled dice images to re-roll a single die
function rerollSingleDie(event) {
    const clickedDieElement = event.currentTarget;
    const dieType = clickedDieElement.dataset.die;
    // Get the original index of this die from the dataset
    const index = parseInt(clickedDieElement.dataset.index);

    // Ensure this is a post-roll die icon
     if (!clickedDieElement.classList.contains('rolled-die')) {
         return;
     }

    // Prevent multiple re-rolls while one is in progress (optional but good practice)
    clickedDieElement.style.pointerEvents = 'none';


    // --- Start Re-roll Animation and Sound ---

    rollSound.currentTime = 0; // Rewind to start
    rollSound.play().catch(e => console.error("Sound playback failed:", e)); // Play sound, catch potential errors

    // Perform the single roll NOW to get the final result
    const newResult = rollDie(dieType);

    // Animation Logic with Falloff (similar to performRoll)
    let intervalTime = 50; // Start fast (milliseconds)
    const intervalIncrease = 15; // How much to increase interval each step
    const maxIntervalTime = 300; // Maximum interval time
    // Random animation duration between 250ms and 1000ms (matching previous roll animation)
    const minDuration = 250; // 0.25 seconds
    const maxDuration = 800; // 0.8 seconds
    const animationDuration = Math.floor(Math.random() * (maxDuration - minDuration + 1)) + minDuration;

    let startTime = Date.now();

    function animateSingle() {
        const elapsed = Date.now() - startTime;

        if (elapsed < animationDuration) {
            // Still animating, show random faces
            clickedDieElement.src = getRandomFaceImage(dieType);

            // Calculate next interval time with falloff
            const progress = elapsed / animationDuration;
            let currentInterval = intervalTime + progress * (maxIntervalTime - intervalTime);
            currentInterval = Math.min(currentInterval, maxIntervalTime); // Cap at max interval

            setTimeout(animateSingle, currentInterval); // Schedule next frame
        } else {
            // Animation finished, show the new result
            let faceToShow = newResult;
             // Adjust for d10 if 10 is represented by face 10 image
             if (dieType === 'd10' && newResult === 10) {
                 faceToShow = 10; // Use 10 if your image is d10_face10.png
             } else if (dieType === 'd10' && newResult === 0) {
                 // If your rollDie function can return 0 for d10s, treat it as 10
                 faceToShow = 10; // Assuming 0 face image is d10_face10.png
             }
            clickedDieElement.src = `../images/${dieType}_face${faceToShow}.png`;

            // --- Update result and sum AFTER animation finishes ---
            // Update the result in the lastRollResults array
            if (index >= 0 && index < lastRollResults.length) {
                 lastRollResults[index].result = newResult;
                 // Update the total sum displayed
                 displayTotalSum();
             } else {
                 console.error("Error: Could not find die index for re-roll update.");
             }
             // ---------------------------------------------------

             // Re-enable clicking after animation
             clickedDieElement.style.pointerEvents = 'auto';
        }
    }

    // Start the animation loop for this single die
    animateSingle();

    // --- End Re-roll Animation and Sound ---
}


// Perform the rolling animation and calculate results
function performRoll() {
  let diceToRollConfig;

  // Determine which configuration to roll
  const totalSelectedVisualDice = Object.values(selectedDice).reduce((sum, count) => sum + count, 0);

  if (totalSelectedVisualDice > 0) {
      // User has selected new dice visually (icons are in resultsArea)
      diceToRollConfig = { ...selectedDice }; // Use the current selection
       // Clear the selected dice icons from the resultsArea before starting animation
       resultsArea.innerHTML = '';
       // Reset selectedDice state after capturing the config
       selectedDice = { d4: 0, d6: 0, d8: 0, d10: 0, d12: 0, d20: 0 };

  } else if (Object.keys(lastRollsConfig).length > 0) {
      // No new selection (resultsArea is empty), but there was a last roll config stored
      diceToRollConfig = { ...lastRollsConfig }; // Use the last config
       resultsArea.innerHTML = ''; // Clear resultsArea in case old results are still there
  } else {
      // Nothing selected (resultsArea empty) and no last roll - should be prevented by button state, but safety check
      console.log("No dice selected and no last roll config.");
      return;
  }

  // Store the config being rolled for potential "Roll Again" (which is now just clicking the button again)
  lastRollsConfig = { ...diceToRollConfig };


  let diceToAnimate = [];
  for (const type in diceToRollConfig) {
    for (let i = 0; i < diceToRollConfig[type]; i++) {
      diceToAnimate.push(type);
    }
  }

  if (diceToAnimate.length === 0) {
       updateRollButtonDisplay(); // Update button state if config was empty
       return; // Nothing to roll
  }


  rollSound.currentTime = 0; // Rewind to start
  rollSound.play().catch(e => console.error("Sound playback failed:", e)); // Play sound, catch potential errors

  const totalDiceCount = diceToAnimate.length;
  let completedRolls = 0;
  let currentRollResults = []; // Store results for this roll

  // Create new image elements for the animation in the now empty resultsArea
  diceToAnimate.forEach((dieType, index) => {
    const dieElement = document.createElement('img');
    dieElement.classList.add('rolled-die'); // Use rolled-die class for animation
    dieElement.dataset.die = dieType; // Store die type on the element
    dieElement.dataset.index = index; // Store the original index for re-rolling

    // Start with a random initial face
    dieElement.src = getRandomFaceImage(dieType);
    dieElement.alt = dieType;
    resultsArea.appendChild(dieElement);

    const finalResult = rollDie(dieType);
    currentRollResults.push({ type: dieType, result: finalResult });

    // Animation Logic with Falloff
    let intervalTime = 50; // Start fast (milliseconds)
    const intervalIncrease = 15; // How much to increase interval each step
    const maxIntervalTime = 300; // Maximum interval time
    // Random animation duration between 250ms and 1000ms
    const minDuration = 250; // 0.25 seconds
    const maxDuration = 1000; // 1.0 seconds
    const animationDuration = Math.floor(Math.random() * (maxDuration - minDuration + 1)) + minDuration;


    let startTime = Date.now();

    function animate() {
      const elapsed = Date.now() - startTime;

      if (elapsed < animationDuration) {
        // Still animating, show random faces
        dieElement.src = getRandomFaceImage(dieType);

        // Calculate next interval time with falloff
         // This falloff calculation now uses the random animationDuration for this specific die
         const progress = elapsed / animationDuration;
         // Simple linear increase of interval based on progress
         let currentInterval = intervalTime + progress * (maxIntervalTime - intervalTime);
         currentInterval = Math.min(currentInterval, maxIntervalTime); // Cap at max interval

        setTimeout(animate, currentInterval); // Schedule next frame
      } else {
        // Animation finished for this die, show final result
         // Find the result for this specific die element based on its index in the animation array
         // This assumes the order in diceToAnimate matches the order of dieElement creation
         const resultForThisDie = currentRollResults[index].result;
         let faceToShow = resultForThisDie;
         // Adjust for d10 if 10 is represented by face 10 image
         if (dieType === 'd10' && resultForThisDie === 10) {
             faceToShow = 10; // Use 10 if your image is d10_face10.png
         } else if (dieType === 'd10' && resultForThisDie === 0) {
             // If your rollDie function can return 0 for d10s, treat it as 10
             faceToShow = 10; // Assuming 0 face image is d10_face10.png
         }
         dieElement.src = `../images/${dieType}_face${faceToShow}.png`;

        // --- Add click listener for re-rolling AFTER animation finishes ---
        dieElement.addEventListener('click', rerollSingleDie);
        // -----------------------------------------------------------------


        completedRolls++;

        if (completedRolls === totalDiceCount) {
            // All dice finished animating
            lastRollResults = currentRollResults; // Store results for display/reference
            displayTotalSum();
             // Sound will likely finish on its own or can be stopped here if needed
             // if (!rollSound.paused) { rollSound.pause(); } // Optional
        }
      }
    }

    animate(); // Start the animation loop
  });

   updateRollButtonDisplay(); // Update button state/text immediately after roll starts
}

// Display the sum of the results
// This function now clears and re-appends the sum element to ensure it's always up-to-date
function displayTotalSum() {
    // Remove any existing sum element first
    const existingSumElement = resultsArea.querySelector('.total-sum');
    if (existingSumElement) {
        existingSumElement.remove();
    }

    if (lastRollResults.length === 0) return;

    let totalSum = lastRollResults.reduce((sum, roll) => {
        // Handle d10 where 10 might be represented as 0 visually but is 10 numerically
        let value = roll.result;
        // Assuming a d10 roll of 10 is numerically 10, even if the image is face 0 or face 10
         if (roll.type === 'd10' && value === 10) {
              value = 10;
         } else if (roll.type === 'd10' && value === 0) {
             // If your rollDie function can return 0 for d10s, treat it as 10
             value = 10;
         }
         return sum + value;
     }, 0);

    const sumElement = document.createElement('div');
    sumElement.classList.add('total-sum'); // Add a class to easily find and remove it later
    sumElement.textContent = `Total: ${totalSum}`;
    sumElement.style.fontWeight = 'bold';
    sumElement.style.marginTop = '10px';
    sumElement.style.width = '100%';
    sumElement.style.textAlign = 'center';
    resultsArea.appendChild(sumElement);
}


// --- Event Listeners ---

// Attach listeners only to the original icons in the selector
originalDiceIcons.forEach(icon => {
  icon.addEventListener('click', handleDiceClick);
  icon.addEventListener('contextmenu', handleDiceClick); // Listen for right-click
});

rollBtn.addEventListener('click', performRoll);


// --- Initialization ---
updateRollButtonDisplay(); // Set initial state of button
