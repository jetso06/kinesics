import os
import cv2
import tkinter as tk
from tkinter import ttk, simpledialog
from PIL import Image, ImageTk
import shutil
import pyautogui
import json
import numpy as np

# Directory and file definitions
gesture_dir = "gestures"
gesture_file = "gesture_key_mapping.json"
current_gesture_index = 0
is_gesture_registered = False
gesture_key_mapping = {}
is_running = False  # Flag to indicate if gesture detection is running
sequence_length = 30  # Number of frames per action sequence

# Add these variables for gesture detection management
last_detected_gesture = None
gesture_cooldown = 500  # milliseconds
last_action_time = 0  # last time the action was performed

# Create the directory to store gesture images if it doesn't exist
if not os.path.exists(gesture_dir):
    os.makedirs(gesture_dir)

# Initialize the webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Create the main tkinter window
root = tk.Tk()
root.title("Hand Gesture Recognition")
root.geometry("900x600")  # Set window size
root.config(bg="#2c3e50")  # Set background color

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
            img = Image.fromarray(frame_rgb)
            img_tk = ImageTk.PhotoImage(image=img)
            canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
            canvas.img_tk = img_tk  # Keep a reference to avoid garbage collection
        
        if is_running:
            # Detect gesture from the current frame
            gesture_id = detect_gesture(frame)
            if gesture_id is not None:
                perform_key_action(gesture_id)

    root.after(10, update_frame)

# Function to detect gestures (template matching example)
def detect_gesture(frame):
    global last_detected_gesture
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert the frame to grayscale for comparison
    detected_gesture_id = None  # Track which gesture was detected

    for gesture_id in gesture_key_mapping:
        gesture_path = os.path.join(gesture_dir, f"gesture_{gesture_id}.png")
        
        # Ensure the gesture image exists before attempting to load it
        if os.path.exists(gesture_path):
            saved_gesture_img = cv2.imread(gesture_path, 0)  # Load the gesture image in grayscale
            saved_gesture_img = cv2.resize(saved_gesture_img, (gray_frame.shape[1], gray_frame.shape[0]))  # Resize gesture to match frame size
            
            # Template matching (use normalized cross-correlation method)
            result = cv2.matchTemplate(gray_frame, saved_gesture_img, cv2.TM_CCOEFF_NORMED)
            threshold = 0.7  # Adjusted threshold for detection accuracy
            loc = np.where(result >= threshold)
            
            if len(loc[0]) > 0:
                detected_gesture_id = gesture_id
                break  # Exit the loop as we found a matching gesture

    return detected_gesture_id

# Function to register a new gesture and assign a key
def register_gesture():
    global current_gesture_index, is_gesture_registered
    print(f'Start capturing video for gesture {current_gesture_index}')
    
    frames = []
    for seq in range(10):  # Capture 10 sequences per gesture
        print(f'Capturing sequence {seq + 1}')
        for _ in range(sequence_length):
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame")
                break
            frames.append(frame)
            cv2.imshow('frame', frame)
            cv2.waitKey(30)

    # Save frames as a sequence for the gesture
    file_path = os.path.join(gesture_dir, f"gesture_{current_gesture_index}.png")
    cv2.imwrite(file_path, frames[-1])  # Save the last frame as the gesture image

    # Ask the user to input the keyboard key for this gesture
    key = simpledialog.askstring("Assign Key", f"Enter a key for Gesture {current_gesture_index + 1}:")
    
    if key:
        # Map the gesture to the provided key
        gesture_key_mapping[current_gesture_index] = key.upper()
        current_gesture_index += 1
        
        # Save the gesture-key mappings to the JSON file
        with open(gesture_file, "w") as f:
            json.dump(gesture_key_mapping, f)
        
        # Update the status label
        status_label.config(text=f"Gesture {current_gesture_index} assigned to key '{key.upper()}'!")
        is_gesture_registered = True

# Function to reset the application and clear registered gestures
def reset_app():
    global current_gesture_index, is_gesture_registered, gesture_key_mapping
    if os.path.exists(gesture_dir):
        shutil.rmtree(gesture_dir)
    os.makedirs(gesture_dir)  # Recreate the folder after deletion
    if os.path.exists(gesture_file):
        os.remove(gesture_file)  # Remove the JSON file
    
    current_gesture_index = 0
    gesture_key_mapping = {}
    is_gesture_registered = False
    status_label.config(text="All gestures have been reset.")
    canvas.delete("all")  # Clear the canvas
    update_frame()  # Resume showing the live camera feed

# Function to simulate key press based on detected gesture
def perform_key_action(gesture_id):
    global last_detected_gesture, last_action_time
    current_time = cv2.getTickCount() / cv2.getTickFrequency() * 1000  # Convert ticks to milliseconds

    if gesture_id in gesture_key_mapping and (gesture_id != last_detected_gesture or (current_time - last_action_time) > gesture_cooldown):
        key = gesture_key_mapping[gesture_id]
        pyautogui.press(key)  # Simulate the key press using pyautogui
        print(f"Performed action for Gesture {gesture_id}: Pressed {key}")
        
        last_detected_gesture = gesture_id  # Update the last detected gesture
        last_action_time = current_time  # Update the last action time

# Function to proceed to the next frame or reset the registration state
def go_home():
    global is_gesture_registered
    status_label.config(text="Proceed to register the next gesture.")
    is_gesture_registered = False

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

button3 = ttk.Button(control_frame, text="New", command=go_home)
button3.grid(row=3, column=0, pady=10, padx=10, sticky="ew")

# Add the "Run" button to start gesture detection
button_run = ttk.Button(control_frame, text="Run", command=run_gestures)
button_run.grid(row=4, column=0, pady=10, padx=10, sticky="ew")

# Label to display status messages
status_label = tk.Label(control_frame, text="", font=("Helvetica", 10), bg="#34495e", fg="white")
status_label.grid(row=5, column=0, pady=10)

# Load existing gestures at startup
load_gestures()

# Start the camera feed update loop
update_frame()

# Start the Tkinter main loop
root.mainloop()

# Release the webcam and close any open windows
cap.release()
cv2.destroyAllWindows()