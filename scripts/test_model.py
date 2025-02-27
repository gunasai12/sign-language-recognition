import cv2
import numpy as np
import tensorflow as tf
import os

# Load trained model
MODEL_PATH = "models/new_sign_language_model.keras"  # Updated model path
print(f"Loading model from: {MODEL_PATH}")
model = tf.keras.models.load_model(MODEL_PATH)

# Get class labels from the processed dataset directory
CLASSES = sorted(os.listdir("processed_dataset"))
print(f"Available classes: {CLASSES}")

# Directory containing test images
TEST_IMAGE_DIR = "test_images"  # Relative path
os.makedirs(TEST_IMAGE_DIR, exist_ok=True)  # Create directory if it doesn't exist

# Function to preprocess image
def preprocess_image(image_path):
    img = cv2.imread(image_path)  # Read in RGB
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")
    
    # Resize to match training input size
    img = cv2.resize(img, (64, 64))
    
    # Convert to RGB (model expects RGB)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Normalize pixel values
    img = img / 255.0
    
    # Add batch dimension
    img = np.expand_dims(img, axis=0)
    
    return img

def test_single_image(image_path):
    try:
        # Preprocess the image
        processed_img = preprocess_image(image_path)
        
        # Make prediction
        prediction = model.predict(processed_img, verbose=0)
        predicted_class = np.argmax(prediction[0])
        confidence = float(prediction[0][predicted_class] * 100)
        
        # Get the class name
        predicted_label = CLASSES[predicted_class]
        
        print(f"\nResults for {os.path.basename(image_path)}:")
        print(f"Predicted Sign: {predicted_label}")
        print(f"Confidence: {confidence:.2f}%")
        
        # Display the image with prediction
        img = cv2.imread(image_path)
        img = cv2.resize(img, (400, 400))  # Resize for display
        cv2.putText(img, f"{predicted_label} ({confidence:.1f}%)", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Show the image
        cv2.imshow('Test Result', img)
        cv2.waitKey(0)  # Wait for key press
        
        return predicted_label, confidence
        
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")
        return None, 0

# Test model on images
test_images = [f for f in os.listdir(TEST_IMAGE_DIR) 
               if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

if not test_images:
    print(f"\nNo images found in {TEST_IMAGE_DIR}. Please add some test images.")
    print("Supported formats: .png, .jpg, .jpeg")
else:
    print(f"\nFound {len(test_images)} test images.")
    
    # Process each test image
    results = []
    for image_name in test_images:
        image_path = os.path.join(TEST_IMAGE_DIR, image_name)
        label, conf = test_single_image(image_path)
        if label:
            results.append((image_name, label, conf))
    
    # Print summary
    if results:
        print("\nTest Summary:")
        print("-" * 50)
        for image_name, label, conf in results:
            print(f"{image_name}: {label} ({conf:.1f}% confidence)")
    
    cv2.destroyAllWindows()  # Clean up windows
