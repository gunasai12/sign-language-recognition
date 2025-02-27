import cv2
import os
import numpy as np

DATASET_PATH = "dataset"
PROCESSED_PATH = "processed_dataset/"

os.makedirs(PROCESSED_PATH, exist_ok=True)

for gesture in os.listdir(DATASET_PATH):
    input_folder = os.path.join(DATASET_PATH, gesture)
    output_folder = os.path.join(PROCESSED_PATH, gesture)
    os.makedirs(output_folder, exist_ok=True)

    for img_name in os.listdir(input_folder):
        img_path = os.path.join(input_folder, img_name)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)  # Convert to grayscale
        img = cv2.resize(img, (64, 64))  # Resize to 64x64

        # Normalize
        img = img / 255.0

        save_path = os.path.join(output_folder, img_name)
        cv2.imwrite(save_path, (img * 255).astype(np.uint8))  # Convert to uint8 before saving
