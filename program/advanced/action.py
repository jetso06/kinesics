import os
import cv2

DATA_DIR = '.data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

number_of_actions = 8 # Number of actions
sequence_length = 30  # Number of frames per action sequence

cap = cv2.VideoCapture(0)

for action in range(number_of_actions):
    action_dir = os.path.join(DATA_DIR, str(action))
    if not os.path.exists(action_dir):
        os.makedirs(action_dir)

    print(f'Collecting data for action {action}')
    print('Press "Q" to start capturing video')

    # Wait for user to get ready
    while True:
        ret, frame = cap.read()
        cv2.putText(frame, 'Press "Q" to start capturing', (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3, cv2.LINE_AA)
        cv2.imshow('frame', frame)
        if cv2.waitKey(25) == ord('q'):
            break

    print(f'Start capturing video for action {action}')

    # Capture frames
    for seq in range(30):  # Capture 10 sequences per action
        print(f'Capturing sequence {seq + 1}')
        frames = []
        for _ in range(sequence_length):
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame")
                break
            frames.append(frame)
            cv2.imshow('frame', frame)
            cv2.waitKey(30)

        # Save frames as a sequence
        sequence_path = os.path.join(action_dir, f'{seq}.avi')
        out = cv2.VideoWriter(sequence_path, cv2.VideoWriter_fourcc(*'XVID'), 10, (frame.shape[1], frame.shape[0]))
        for f in frames:
            out.write(f)
        out.release()

cap.release()
cv2.destroyAllWindows()