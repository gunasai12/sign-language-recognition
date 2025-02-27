import cv2
import os

# Define dataset directory
DATASET_PATH = "dataset/"
GESTURE = "Welcome"  # Change this to the gesture name
SAVE_PATH = os.path.join(DATASET_PATH, GESTURE)
os.makedirs(SAVE_PATH, exist_ok=True)

cap = cv2.VideoCapture(0)  # Try 0, 1, or -1

if not cap.isOpened():
    print("❌ ERROR: Webcam not detected. Try changing VideoCapture(0) to VideoCapture(1) or -1.")
    exit()

count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ ERROR: Failed to capture video. Check your webcam.")
        break
    
    # Draw rectangle for hand placement
    cv2.rectangle(frame, (100, 100), (400, 400), (255, 0, 0), 2)

    # Crop hand region and save
    hand = frame[100:400, 100:400]
    filename = os.path.join(SAVE_PATH, f"{count}.jpg")
    cv2.imwrite(filename, hand)
    count += 1

    cv2.imshow("Frame", frame)

    # Quit on 'q' or after capturing 100 images
    if cv2.waitKey(500) & 0xFF == ord('q') or count >= 50:
        break

cap.release()
cv2.destroyAllWindows()
print(f"✅ {count} images saved in {SAVE_PATH}")
