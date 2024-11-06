import cv2
import mediapipe as mp
import pyautogui
import numpy as np

# Initialize Mediapipe hand tracking
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

# Capture video feed
cap = cv2.VideoCapture(0)

# Define gesture descriptions
gesture_descriptions = {
    "click": "Click: Bring thumb and index finger together.",
    "volume_up": "Volume Up: Bring thumb and middle finger together.",
    "volume_down": "Volume Down: Bring thumb and ring finger together.",
    "move_cursor": "Move Cursor: Extend index finger alone.",
    "unknown": "Unknown: Gesture not recognized."
}

# Helper function to recognize gestures
def recognize_gesture(landmarks):
    thumb_tip = landmarks[4]      # Thumb tip
    index_tip = landmarks[8]      # Index finger tip
    middle_tip = landmarks[12]    # Middle finger tip
    ring_tip = landmarks[16]      # Ring finger tip

    # Calculate distances for gesture recognition
    thumb_index_dist = np.linalg.norm(np.array([thumb_tip.x, thumb_tip.y]) - np.array([index_tip.x, index_tip.y]))
    thumb_middle_dist = np.linalg.norm(np.array([thumb_tip.x, thumb_tip.y]) - np.array([middle_tip.x, middle_tip.y]))
    thumb_ring_dist = np.linalg.norm(np.array([thumb_tip.x, thumb_tip.y]) - np.array([ring_tip.x, ring_tip.y]))

    # Define gesture thresholds
    if thumb_index_dist < 0.05:
        return "click"
    elif thumb_middle_dist < 0.05:
        return "volume_up"
    elif thumb_ring_dist < 0.05:
        return "volume_down"
    elif thumb_index_dist > 0.2:
        return "move_cursor"
    else:
        return "unknown"

# Loop for video feed and gesture recognition
while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)  # Mirror the frame
    h, w, _ = frame.shape  # Dimensions of the frame

    # Convert the frame to RGB for Mediapipe processing
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    # Check for detected hands and landmarks
    recognized_gesture = "unknown"  # Default gesture
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw hand landmarks on the frame
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Extract landmark coordinates
            landmarks = hand_landmarks.landmark
            recognized_gesture = recognize_gesture(landmarks)

            # Gesture-based actions
            if recognized_gesture == "click":
                pyautogui.click()
            elif recognized_gesture == "volume_up":
                pyautogui.press("volumeup")
            elif recognized_gesture == "volume_down":
                pyautogui.press("volumedown")
            elif recognized_gesture == "move_cursor":
                # Move cursor based on index finger position
                index_finger = landmarks[8]
                cursor_x = int(index_finger.x * w)
                cursor_y = int(index_finger.y * h)
                pyautogui.moveTo(cursor_x, cursor_y)

    # Prepare to display gesture descriptions on the right side
    right_frame = np.zeros((h, 400, 3), dtype=np.uint8)  # Create a blank image for descriptions
    cv2.putText(right_frame, "Gesture Descriptions:", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Show the recognized gesture description
    for i, (gesture, description) in enumerate(gesture_descriptions.items()):
        color = (0, 255, 0) if gesture == recognized_gesture else (255, 255, 255)
        cv2.putText(right_frame, description, (10, 70 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)

    # Combine frames: left (camera) and right (descriptions)
    combined_frame = np.hstack((frame, right_frame))

    # Show combined output
    cv2.imshow("Hand Gesture Recognition", combined_frame)

    # Exit loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()