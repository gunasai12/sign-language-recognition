# Sign Language Detection Video Call App

A real-time video calling application with integrated sign language detection.

## Features
- Real-time video calls between two users
- Sign language detection for deaf users
- Visual feedback for detected signs
- Support for multiple sign gestures

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd sign-language-recognition
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows
source .venv/bin/activate  # On Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Access the application:
   - On the host machine: http://localhost:5000
   - From other devices: http://<host-ip>:5000 (e.g., http://192.168.80.37:5000)

## Usage Instructions

1. Open the application in two different browsers or devices
2. In the first window:
   - Select "I am deaf and will use sign language"
   - Enter a room ID
   - Click "Join Room"
3. In the second window:
   - Select "I am not deaf and will read sign language"
   - Enter the same room ID
   - Click "Join Room"
4. For the deaf user:
   - Position your hands within the green box
   - Make signs clearly
5. For the non-deaf user:
   - Watch for detected signs below the video

## Supported Signs
The application can detect the following signs:
- [List of signs from your dataset]

## Requirements
- Python 3.8 or higher
- Webcam
- Modern web browser (Chrome recommended)
- Network connectivity between devices
