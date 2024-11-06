import cv2
import tkinter as tk
from tkinter import ttk, simpledialog
from PIL import Image, ImageTk
import os
import shutil
import pyautogui
import json
import numpy as np
import mediapipe as mp
import time

# Initialize cooldown timer and smoothing parameters
cooldown_time = 1.0  # Time in seconds between allowed presses
last_press_time = time.time()
frames_with_gesture = 0
required_frames = 5  # Number of consecutive frames to confirm a gesture

# Directory and file definitions
gesture_dir = "gestures"
gesture_file = "gesture_key_mapping.json"
current_gesture_index = 0
is_gesture_registered = False
gesture_key_mapping = {}
is_running = False  # Flag to indicate if gesture detection is running

# Initialize MediaPipe hand detector
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils  # Utility for drawing landmarks

# Create the directory to store gesture images if it doesn't exist
if not os.path.exists(gesture_dir):
    os.makedirs(gesture_dir)

# Initialize the webcam
cap = cv2.VideoCapture(0)

# Create the main tkinter window
root = tk.Tk()
root.title("Hand Gesture Recognition")
root.geometry("1000x600")  # Set window size
root.config(bg="#2c3e50")  # Set background color

# Define confidence threshold for gesture recognition
confidence_threshold = 0.8  # Adjust this based on your needs

# Load existing gestures from the JSON file if available
def load_gestures():
    global gesture_key_mapping, current_gesture_index
    if os.path.exists(gesture_file):
        with open(gesture_file, "r") as f:
            gesture_key_mapping = json.load(f)
            current_gesture_index = len(gesture_key_mapping)
        status_label.config(text="Loaded existing gestures.")
    else:
        status_label.config(text="No saved gestures found.")

# Function to update the camera feed in the Tkinter canvas
def update_frame():
    if not is_gesture_registered:  # Only update the feed if no gesture is registered
        ret, frame = cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Use MediaPipe to detect hand landmarks
            results = hands.process(frame_rgb)
            
            # Draw landmarks on the frame if hands are detected
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Convert frame to display in tkinter
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            img_tk = ImageTk.PhotoImage(image=img)
            canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
            canvas.img_tk = img_tk  # Keep a reference to avoid garbage collection
        
        if is_running:
            # Detect gesture from the current frame
            gesture_id = detect_gesture(frame, results)
            if gesture_id is not None:
                perform_key_action(gesture_id)  # Only press key if gesture is detected
    
    root.after(10, update_frame)
    
# Function to detect gestures using hand landmarks
def detect_gesture(frame, results):
    global last_detected_gesture_id, frames_with_gesture
    if not results.multi_hand_landmarks:
        confidence_label.config(text="No hand detected. Confidence: N/A")
        last_detected_gesture_id = None
        frames_with_gesture = 0  # Reset count if no hand is detected
        return None

    hand_landmarks = results.multi_hand_landmarks[0]  # Assume one hand detected
    landmarks = []
    for lm in hand_landmarks.landmark:
        landmarks.append([lm.x, lm.y, lm.z])

    # Feature extraction: Normalize the landmarks (You can extract more features here if needed)
    # For example, you can compute the relative distances between key points, angles, etc.
    feature_vector = np.array([lm[0] for lm in landmarks] + [lm[1] for lm in landmarks] + [lm[2] for lm in landmarks])

    best_match_id = None
    best_match_value = 0

    # Compare the extracted feature vector with the previously stored gesture vectors
    for gesture_id, key in gesture_key_mapping.items():
        gesture_path = os.path.join(gesture_dir, f"gesture_{gesture_id}.json")
        
        if os.path.exists(gesture_path):
            # Load the pre-stored feature vector for the gesture
            with open(gesture_path, "r") as f:
                saved_feature_vector = np.array(json.load(f))

            # Calculate the similarity (cosine similarity, Euclidean distance, etc.)
            similarity = np.dot(feature_vector, saved_feature_vector) / (np.linalg.norm(feature_vector) * np.linalg.norm(saved_feature_vector))
            
            if similarity > best_match_value and similarity >= confidence_threshold:
                best_match_value = similarity
                best_match_id = gesture_id

    if best_match_id is not None and best_match_value >= confidence_threshold:
        frames_with_gesture += 1  # Count frames with detected gesture
        if frames_with_gesture >= required_frames:
            last_detected_gesture_id = best_match_id
            matched_key = gesture_key_mapping[best_match_id]
            confidence_label.config(text=f"Confidence: {best_match_value:.2f} - Key: {matched_key}")
            return best_match_id
    else:
        confidence_label.config(text="No gesture detected. Confidence: N/A")
        last_detected_gesture_id = None
        frames_with_gesture = 0  # Reset if no consistent gesture is detected
    return None

# Function to register a new gesture and assign a key
def register_gesture():
    global current_gesture_index, is_gesture_registered
    ret, frame = cap.read()
    if ret:
        # Save the current frame as an image in the gesture folder
        file_path = os.path.join(gesture_dir, f"gesture_{current_gesture_index}.png")
        cv2.imwrite(file_path, frame)
        
        # Extract hand landmarks and create a feature vector
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            landmarks = [[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark]
            feature_vector = np.array([lm[0] for lm in landmarks] + [lm[1] for lm in landmarks] + [lm[2] for lm in landmarks])
            
            # Save the feature vector to a JSON file
            gesture_feature_path = os.path.join(gesture_dir, f"gesture_{current_gesture_index}.json")
            with open(gesture_feature_path, "w") as f:
                json.dump(feature_vector.tolist(), f)
        
        # Ask the user to input the keyboard key for this gesture
        key = simpledialog.askstring("Assign Key", f"Enter a key for Gesture {current_gesture_index+1}:")
        
        if key:
            # Map the gesture to the provided key
            gesture_key_mapping[current_gesture_index] = key.upper()
            current_gesture_index += 1
            
            # Save the gesture-key mappings to the JSON file
            with open(gesture_file, "w") as f:
                json.dump(gesture_key_mapping, f)
            
            # Update the status label
            status_label.config(text=f"Gesture {current_gesture_index} assigned to key '{key.upper()}'!")
            
            # Show the saved gesture image in the canvas
            img = Image.open(file_path)
            img = img.resize((640, 480))  # Resize the image to fit the canvas
            img_tk = ImageTk.PhotoImage(img)
            canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
            canvas.img_tk = img_tk  # Keep a reference
            
            is_gesture_registered = True

# Rest of the code remains the same...


# Function to reset the application and clear registered gestures
def reset_app():
    global current_gesture_index, is_gesture_registered, gesture_key_mapping
    # Delete all previously saved gesture images and the JSON file
    if os.path.exists(gesture_dir):
        shutil.rmtree(gesture_dir)
    os.makedirs(gesture_dir)  # Recreate the folder after deletion
    
    if os.path.exists(gesture_file):
        os.remove(gesture_file)  # Remove the JSON file
    
    # Reset the application state
    current_gesture_index = 0
    gesture_key_mapping = {}
    is_gesture_registered = False
    status_label.config(text="All gestures have been reset.")
    canvas.delete("all")  # Clear the canvas
    update_frame()  # Resume showing the live camera feed

# Function to simulate key press based on detected gesture
def perform_key_action(gesture_id):
    global last_press_time
    if gesture_id is not None and gesture_id in gesture_key_mapping:
        current_time = time.time()
        if current_time - last_press_time >= cooldown_time:
            key = gesture_key_mapping[gesture_id]
            pyautogui.press(key)
            last_press_time = current_time  # Update the last press time
            print(f"Performed action for Gesture {gesture_id}: Pressed {key}")

# Function to proceed to the next frame or reset the registration state
def go_home():
    global is_gesture_registered
    status_label.config(text="Proceed to register the next gesture.")  # Update status
    is_gesture_registered = False  # Allow the camera feed to start again

# Function to start detecting gestures when the "Run" button is clicked
def run_gestures():
    global is_running
    is_running = True
    status_label.config(text="Gesture detection started!")

# Main frame to hold everything
main_frame = tk.Frame(root, bg="#34495e", padx=10, pady=10)
main_frame.pack(fill="both", expand=True)

# Create a frame for the camera feed
camera_frame = tk.Frame(main_frame, width=640, height=480, bg="#ecf0f1", bd=2, relief="sunken")
camera_frame.grid(row=0, column=0, padx=20, pady=20)

# Create a canvas for displaying the camera feed inside the camera frame
canvas = tk.Canvas(camera_frame, width=640, height=480)
canvas.pack()

# Create a control frame for buttons and labels
control_frame = tk.Frame(main_frame, bg="#34495e")
control_frame.grid(row=0, column=1, padx=20, pady=20, sticky="n")
# Create a label to display the confidence level and matched key
confidence_label = tk.Label(control_frame, text="Confidence: N/A", font=("Helvetica", 12), fg="white", bg="#34495e")
confidence_label.grid(row=6, column=0, pady=10)



# Add a title to the control panel
control_title = tk.Label(control_frame, text="Controls", font=("Helvetica", 16), fg="white", bg="#34495e")
control_title.grid(row=0, column=0, pady=10)

# Create buttons with styled appearance
style = ttk.Style()
style.configure("TButton", font=("Helvetica", 12), padding=10, background="#1abc9c")

button1 = ttk.Button(control_frame, text="Register Gesture", command=register_gesture)
button1.grid(row=1, column=0, pady=10, padx=10, sticky="ew")

button2 = ttk.Button(control_frame, text="Reset", command=reset_app)
button2.grid(row=2, column=0, pady=10, padx=10, sticky="ew")

button3 = ttk.Button(control_frame, text="Compile", command=go_home)
button3.grid(row=3, column=0, pady=10, padx=10, sticky="ew")

# Add the "Run" button to start gesture detection
button_run = ttk.Button(control_frame, text="Run", command=run_gestures)
button_run.grid(row=4, column=0, pady=10, padx=10, sticky="ew")

# Create a status label to display messages to the user
status_label = tk.Label(control_frame, text="No gestures registered.", font=("Helvetica", 12), fg="white", bg="#34495e")
status_label.grid(row=5, column=0, pady=20)

# Start updating the camera feed
load_gestures()  # Load saved gestures on startup
update_frame()

# Start the Tkinter event loop
root.mainloop()

# Release the webcam and close OpenCV windows
cap.release()
cv2.destroyAllWindows()