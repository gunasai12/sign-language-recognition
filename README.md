# Sign Language Detection Video Call Application

A real-time sign language detection application that enables seamless communication between deaf and non-deaf users through video calls.

## Features

- Real-time video calls using WebRTC
- Live sign language detection using TensorFlow.js
- Instant text translation of detected signs
- Secure peer-to-peer communication
- Room-based connection system
- Responsive design for all devices

## Demo

Visit our live demo: [Sign Language Detection App](https://sign-language-recognition.onrender.com)

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 14+
- Web browser (Chrome or Firefox recommended)
- Webcam and microphone

### Installation

1. Clone the repository:
```bash
git clone https://github.com/gunasai12/sign-language-recognition.git
cd sign-language-recognition
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the application:
```bash
python app.py
```

4. Open your browser and visit:
```
http://localhost:5000
```

## Usage Guide

### For Deaf Users

1. Open the application
2. Select "I am deaf and will use sign language"
3. Click "Create Room"
4. Share the Room ID with the other person
5. Make signs within the detection box
6. Watch for detection confirmation

### For Non-deaf Users

1. Open the application
2. Select "I am not deaf and will read sign language"
3. Enter the Room ID shared with you
4. Click "Join Room"
5. View the real-time sign language translations

## Technology Stack

- **Frontend**:
  - HTML5, CSS3, JavaScript
  - WebRTC for peer-to-peer video
  - TensorFlow.js for sign detection
  - Socket.IO client for real-time communication

- **Backend**:
  - Flask (Python web framework)
  - Flask-SocketIO for WebSocket support
  - TensorFlow for model serving

## Development

### Project Structure

```
sign-language-recognition/
├── app.py              # Flask application
├── requirements.txt    # Python dependencies
├── static/
│   ├── style.css      # Application styles
│   ├── webrtc.js      # WebRTC implementation
│   └── detection.js   # Sign detection logic
├── templates/
│   └── index.html     # Main application page
└── models/            # TensorFlow models
```

### Running Tests

```bash
python -m pytest tests/
```

## Deployment

### Deploy to Render

1. Fork this repository
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Use the following settings:
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`

### Environment Variables

- `PORT`: Server port (default: 5000)
- `DEBUG`: Debug mode (default: False)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Troubleshooting

### Common Issues

1. **Camera Access Denied**
   - Check browser permissions
   - Ensure no other app is using the camera

2. **Connection Failed**
   - Verify both users are using the same Room ID
   - Check internet connectivity
   - Ensure WebRTC is not blocked

3. **Detection Not Working**
   - Ensure good lighting
   - Keep hands within the detection box
   - Check browser console for errors

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- TensorFlow team for the sign language detection model
- WebRTC project for real-time communication capabilities
- Flask team for the web framework

## Contact

- GitHub: [@gunasai12](https://github.com/gunasai12)
- Project Link: [https://github.com/gunasai12/sign-language-recognition](https://github.com/gunasai12/sign-language-recognition)
