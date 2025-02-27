# Real-Time Sign Language Detection in Video Calls

## Project Overview
This innovative application combines real-time video calling with sign language detection, creating a bridge between deaf and non-deaf users. The system uses deep learning to recognize sign language gestures during video calls, making communication more accessible and inclusive.

## Key Features
1. **Real-Time Video Calling**
   - Peer-to-peer video communication
   - Low-latency streaming
   - Room-based connection system
   - Automatic connection recovery

2. **Sign Language Detection**
   - Real-time sign language recognition
   - High-accuracy gesture detection
   - Visual feedback for detected signs
   - Support for multiple sign gestures

3. **User Interface**
   - Clean and intuitive design
   - Connection status indicators
   - Detection result display
   - Easy room joining system

## Technical Architecture

### Frontend Components
1. **WebRTC Implementation (`webrtc.js`)**
   - Handles peer-to-peer connections
   - Manages video streams
   - Implements room-based networking
   - Handles connection state

2. **Detection System (`detection.js`)**
   - Captures video frames
   - Processes images for detection
   - Communicates with backend
   - Displays detection results

3. **User Interface (`index.html`, `style.css`)**
   - Responsive design
   - Status indicators
   - Video displays
   - Control buttons

### Backend Components
1. **Flask Server (`app.py`)**
   - WebSocket communication
   - HTTP routing
   - Room management
   - Error handling

2. **Machine Learning Model**
   - TensorFlow-based CNN
   - Trained on sign language dataset
   - Real-time inference
   - High accuracy predictions

3. **Image Processing (`preprocess.py`)**
   - Frame extraction
   - Image normalization
   - ROI selection
   - Data augmentation

## Technology Stack
- **Frontend**:
  - HTML5/CSS3/JavaScript
  - WebRTC
  - Socket.IO Client
  - Canvas API

- **Backend**:
  - Python 3.8+
  - Flask
  - TensorFlow
  - OpenCV
  - Socket.IO

- **Development Tools**:
  - Git for version control
  - Virtual environment for dependency management
  - Chrome DevTools for debugging

## Implementation Details

### Sign Language Detection
1. **Preprocessing Pipeline**
   ```python
   def preprocess_image(frame):
       # Extract ROI from center
       height, width = frame.shape[:2]
       center_x, center_y = width // 2, height // 2
       roi_size = min(width, height) // 2
       
       # Get region of interest
       start_x = center_x - roi_size // 2
       start_y = center_y - roi_size // 2
       roi = frame[start_y:start_y+roi_size, start_x:start_x+roi_size]
       
       # Normalize and resize
       roi = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
       resized = cv2.resize(roi, (64, 64))
       normalized = resized / 255.0
       
       return normalized
   ```

2. **Model Architecture**
   - Convolutional Neural Network
   - Input shape: (64, 64, 3)
   - Multiple conv2d and maxpooling layers
   - Dense layers for classification
   - Softmax output for gesture prediction

### WebRTC Implementation
1. **Connection Setup**
   ```javascript
   const configuration = {
       iceServers: [
           { urls: 'stun:stun.l.google.com:19302' },
           { urls: 'stun:stun1.l.google.com:19302' }
       ]
   };
   ```

2. **Room Management**
   - Unique room IDs for each session
   - User type identification
   - Connection state tracking
   - Automatic cleanup

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Webcam
- Modern web browser (Chrome recommended)
- Network connectivity between devices

### Installation Steps
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd sign-language-recognition
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
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
   - Local: http://localhost:3000
   - Network: http://<your-ip>:3000

## Usage Guide

### For Deaf Users
1. Open the application
2. Select "I am deaf and will use sign language"
3. Enter a room ID
4. Position yourself in the camera view
5. Make signs within the detection box
6. Watch for confirmation of detected signs

### For Non-Deaf Users
1. Open the application
2. Select "I am not deaf and will read sign language"
3. Enter the same room ID
4. Watch for detected signs below the video
5. Communicate through video as normal

## Future Enhancements
1. **Model Improvements**
   - Support for more sign languages
   - Continuous gesture recognition
   - Higher accuracy through more training data
   - Real-time hand tracking

2. **User Experience**
   - Mobile app development
   - Customizable UI
   - Gesture history
   - User profiles

3. **Technical Features**
   - End-to-end encryption
   - Cloud deployment
   - Multiple participant support
   - Recording and playback

## Troubleshooting

### Common Issues and Solutions
1. **Connection Problems**
   - Check network connectivity
   - Verify firewall settings
   - Ensure both users are on the same room ID
   - Try refreshing the page

2. **Detection Issues**
   - Ensure good lighting
   - Position hands within the detection box
   - Make clear, deliberate gestures
   - Check camera permissions

3. **Video Quality**
   - Check internet bandwidth
   - Close other bandwidth-heavy applications
   - Try lowering video quality
   - Ensure camera is working properly

## Security Considerations
- WebRTC peer-to-peer encryption
- Room-based access control
- Input validation
- Error handling
- Secure WebSocket connections

## Performance Optimization
- Efficient frame capture
- Optimized model inference
- Minimal network overhead
- Responsive UI design

## Conclusion
This project demonstrates the potential of combining modern web technologies with machine learning to create accessible communication tools. The real-time sign language detection during video calls opens new possibilities for inclusive communication in various settings, from personal conversations to professional meetings.
