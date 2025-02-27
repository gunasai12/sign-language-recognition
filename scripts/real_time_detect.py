import cv2
import numpy as np
import tensorflow as tf
import os

# Load model
MODEL_PATH = "models/new_sign_language_model.keras"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found at {MODEL_PATH}. Please make sure the model is trained and saved correctly.")

model = tf.keras.models.load_model(MODEL_PATH)

# Get classes from processed dataset to ensure consistency
CLASSES = sorted(os.listdir("processed_dataset"))
print(f"Loaded model. Available classes: {CLASSES}")

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Could not open webcam. Please make sure it's connected and not being used by another application.")

# Create window and set it to a reasonable size
cv2.namedWindow("Sign Detection", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Sign Detection", 800, 600)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame from webcam")
        break

    # Draw hand region
    roi_size = 300
    h, w = frame.shape[:2]
    x = w//2 - roi_size//2
    y = h//2 - roi_size//2
    cv2.rectangle(frame, (x, y), (x + roi_size, y + roi_size), (255, 0, 0), 2)
    
    # Extract and preprocess hand region
    hand = frame[y:y+roi_size, x:x+roi_size]
    hand = cv2.resize(hand, (64, 64))
    hand = cv2.cvtColor(hand, cv2.COLOR_BGR2RGB)  # Convert to RGB
    hand = np.expand_dims(hand, axis=0) / 255.0

    # Predict
    prediction = model.predict(hand, verbose=0)  # Disable verbose output
    pred_idx = np.argmax(prediction)
    confidence = np.max(prediction) * 100
    
    if pred_idx < len(CLASSES):
        label = CLASSES[pred_idx]
        # Display result with confidence
        text = f"{label} ({confidence:.1f}%)"
        cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    else:
        cv2.putText(frame, "Unknown", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Sign Detection", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
