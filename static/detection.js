const detectionCanvas = document.getElementById('detectionCanvas');
const detectedSignElement = document.getElementById('detectedSign');

// Create a canvas to capture video frames
let canvas = null;
let ctx = null;

// Set canvas size to match model input
detectionCanvas.width = 64;
detectionCanvas.height = 64;

let model = null;

// Load the TensorFlow.js model
async function loadModel() {
    try {
        model = await tf.loadLayersModel('/static/model/model.json');
        console.log('Sign language detection model loaded');
    } catch (error) {
        console.error('Error loading model:', error);
    }
}

let socket = io('http://localhost:3000', {
    transports: ['websocket'],
    reconnection: true,
    reconnectionAttempts: 5,
    reconnectionDelay: 1000
});

let isDetecting = false;
let detectionInterval = null;
const FPS = 2; // Frames per second for detection

// UI Elements
const localVideo = document.getElementById('localVideo');
const startButton = document.getElementById('startDetection');
const stopButton = document.getElementById('stopDetection');
const connectionStatus = document.getElementById('connectionStatus');
const detectionStatus = document.getElementById('detectionStatus');
const detectionResult = document.getElementById('detectionResult');
const detectionHistory = document.getElementById('detectionHistory');

// Canvas setup for frame capture
const captureCanvas = document.createElement('canvas');
const captureCtx = captureCanvas.getContext('2d');

// Initialize camera
async function initializeCamera() {
    try {
        const constraints = {
            video: {
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: 'user'
            },
            audio: false
        };

        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        if (localVideo) {
            localVideo.srcObject = stream;
            await localVideo.play();
            
            // Set canvas size based on video dimensions
            captureCanvas.width = localVideo.videoWidth;
            captureCanvas.height = localVideo.videoHeight;
            
            console.log('Camera initialized successfully');
            return true;
        }
    } catch (error) {
        console.error('Error accessing camera:', error);
        alert('Failed to access camera. Please check permissions.');
        return false;
    }
}

// Socket event handlers
socket.on('connect', () => {
    console.log('Connected to server');
    updateConnectionStatus(true);
    enableControls(true);
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
    updateConnectionStatus(false);
    enableControls(false);
    stopDetection();
});

socket.on('detection_result', (data) => {
    console.log('Detection result:', data);
    updateDetectionResult(data);
    addToHistory(data);
});

socket.on('detection_error', (data) => {
    console.error('Detection error:', data.error);
    showError(data.error);
});

// UI update functions
function updateConnectionStatus(connected) {
    if (connectionStatus) {
        connectionStatus.innerHTML = connected ? 
            '<i class="fas fa-check-circle"></i> Connected' :
            '<i class="fas fa-times-circle"></i> Disconnected';
        connectionStatus.className = `status-value ${connected ? 'connected' : 'disconnected'}`;
    }
}

function updateDetectionStatus(active) {
    if (detectionStatus) {
        detectionStatus.innerHTML = active ?
            '<i class="fas fa-video"></i> Active' :
            '<i class="fas fa-video-slash"></i> Inactive';
        detectionStatus.className = `status-value ${active ? 'active' : 'inactive'}`;
    }
}

function updateDetectionResult(result) {
    if (detectionResult && result) {
        const confidence = (result.confidence * 100).toFixed(1);
        detectionResult.innerHTML = `
            <div class="result-label">${result.label}</div>
            <div class="result-confidence">${confidence}%</div>
        `;
        detectionResult.className = 'detection-result active';
    }
}

function showError(message) {
    if (detectionResult) {
        detectionResult.innerHTML = `<div class="error-message">${message}</div>`;
        detectionResult.className = 'detection-result error';
    }
}

function enableControls(enabled) {
    if (startButton) {
        startButton.disabled = !enabled || isDetecting;
    }
    if (stopButton) {
        stopButton.disabled = !enabled || !isDetecting;
    }
}

// Frame capture and detection
function captureFrame() {
    if (!localVideo || !localVideo.videoWidth) return null;

    try {
        // Draw the current frame
        captureCtx.drawImage(localVideo, 0, 0, captureCanvas.width, captureCanvas.height);
        
        // Convert to base64
        return captureCanvas.toDataURL('image/jpeg', 0.8);
    } catch (error) {
        console.error('Error capturing frame:', error);
        return null;
    }
}

// Start detection
function startDetection() {
    if (!localVideo || isDetecting) return;
    
    isDetecting = true;
    updateDetectionStatus(true);
    enableControls(true);
    
    detectionInterval = setInterval(() => {
        const frame = captureFrame();
        if (frame) {
            socket.emit('detect_sign', { image: frame });
        }
    }, 1000 / FPS);
}

// Stop detection
function stopDetection() {
    isDetecting = false;
    updateDetectionStatus(false);
    enableControls(true);
    
    if (detectionInterval) {
        clearInterval(detectionInterval);
        detectionInterval = null;
    }
}

// History management
function addToHistory(result) {
    if (!detectionHistory) return;
    
    const entry = document.createElement('div');
    entry.className = 'history-entry';
    
    const confidence = Math.round(result.confidence * 100);
    entry.innerHTML = `
        <i class="fas fa-clock"></i>
        <span class="time">${new Date().toLocaleTimeString()}</span>
        <span class="label">${result.label}</span>
        <span class="confidence">${confidence}%</span>
    `;
    
    detectionHistory.insertBefore(entry, detectionHistory.firstChild);
    
    // Limit history items
    while (detectionHistory.children.length > 10) {
        detectionHistory.removeChild(detectionHistory.lastChild);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Initializing detection system...');
    
    // Setup button event listeners
    if (startButton) {
        startButton.addEventListener('click', startDetection);
        startButton.disabled = true;
    }
    
    if (stopButton) {
        stopButton.addEventListener('click', stopDetection);
        stopButton.disabled = true;
    }
    
    // Initialize camera
    const cameraReady = await initializeCamera();
    if (cameraReady) {
        console.log('System ready for detection');
    }
});
