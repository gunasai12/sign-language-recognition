from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import os
import json
import base64
import numpy as np
from PIL import Image
import io
import cv2
import tensorflow as tf
import logging
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Store active rooms
rooms = {}

# Load the model
try:
    model_path = 'models/new_sign_language_model.keras'
    if os.path.exists(model_path):
        model = tf.keras.models.load_model(model_path)
        logger.info("Model loaded successfully")
    else:
        logger.error(f"Model not found at: {model_path}")
        model = None
except Exception as e:
    logger.error(f"Error loading model: {e}")
    model = None

# Get class names
try:
    class_names = sorted(os.listdir("processed_dataset")) if os.path.exists("processed_dataset") else []
    logger.info(f"Loaded {len(class_names)} classes: {class_names}")
except Exception as e:
    logger.error(f"Error loading classes: {e}")
    class_names = []

@app.route('/')
def index():
    return render_template('index.html', classes=class_names)

# WebRTC Signaling
@socketio.on('create_room')
def on_create_room():
    room_id = str(uuid.uuid4())[:8]
    join_room(room_id)
    rooms[room_id] = {
        'creator': request.sid,
        'peers': [request.sid]
    }
    logger.info(f"Room created: {room_id}")
    emit('room_created', room_id)

@socketio.on('join_room')
def on_join_room(room_id):
    if room_id in rooms:
        join_room(room_id)
        rooms[room_id]['peers'].append(request.sid)
        logger.info(f"User {request.sid} joined room: {room_id}")
        emit('room_joined', room_id)
    else:
        emit('error', {'message': 'Room not found'})

@socketio.on('offer')
def on_offer(data):
    room_id = data.get('roomId')
    if room_id in rooms:
        emit('offer', data.get('offer'), room=room_id, skip_sid=request.sid)
        logger.info(f"Offer forwarded in room: {room_id}")

@socketio.on('answer')
def on_answer(data):
    room_id = data.get('roomId')
    if room_id in rooms:
        emit('answer', data.get('answer'), room=room_id, skip_sid=request.sid)
        logger.info(f"Answer forwarded in room: {room_id}")

@socketio.on('ice_candidate')
def on_ice_candidate(data):
    room_id = data.get('roomId')
    if room_id in rooms:
        emit('ice_candidate', data.get('candidate'), room=room_id, skip_sid=request.sid)
        logger.info(f"ICE candidate forwarded in room: {room_id}")

@socketio.on('disconnect')
def on_disconnect():
    for room_id in list(rooms.keys()):
        if request.sid in rooms[room_id]['peers']:
            rooms[room_id]['peers'].remove(request.sid)
            if not rooms[room_id]['peers']:
                del rooms[room_id]
            else:
                emit('peer_disconnected', room=room_id, skip_sid=request.sid)
            leave_room(room_id)
            logger.info(f"User {request.sid} left room: {room_id}")

# Sign Detection
def preprocess_image(image_data):
    try:
        # Remove data URL prefix if present
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to numpy array
        image_np = np.array(image)
        
        # Convert BGR to RGB if needed
        if len(image_np.shape) == 3 and image_np.shape[2] == 3:
            image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        
        # Extract ROI (center region)
        height, width = image_np.shape[:2]
        center_x, center_y = width // 2, height // 2
        roi_size = min(width, height) // 2
        
        start_x = center_x - roi_size
        start_y = center_y - roi_size
        end_x = start_x + roi_size * 2
        end_y = start_y + roi_size * 2
        
        roi = image_np[start_y:end_y, start_x:end_x]
        
        # Resize to model input size
        resized = cv2.resize(roi, (64, 64))
        
        # Normalize
        normalized = resized.astype(np.float32) / 255.0
        
        # Add batch dimension
        preprocessed = np.expand_dims(normalized, axis=0)
        
        return preprocessed
    except Exception as e:
        logger.error(f"Error preprocessing image: {e}")
        return None

@socketio.on('detect_sign')
def detect_sign(data):
    try:
        if not model:
            logger.error("Model not loaded")
            emit('detection_error', {'error': 'Model not loaded'})
            return

        if not data or 'image' not in data:
            logger.error("No image data received")
            emit('detection_error', {'error': 'No image data received'})
            return

        # Preprocess image
        preprocessed = preprocess_image(data['image'])
        if preprocessed is None:
            logger.error("Image preprocessing failed")
            emit('detection_error', {'error': 'Image preprocessing failed'})
            return

        # Make prediction
        prediction = model.predict(preprocessed, verbose=0)
        predicted_class_idx = np.argmax(prediction[0])
        confidence = float(prediction[0][predicted_class_idx])

        if predicted_class_idx >= len(class_names):
            logger.error(f"Invalid class index: {predicted_class_idx}")
            emit('detection_error', {'error': 'Invalid prediction'})
            return

        result = {
            'label': class_names[predicted_class_idx],
            'confidence': confidence
        }

        # Emit result to all users in the room
        room_id = data.get('roomId')
        if room_id and room_id in rooms:
            emit('detection_result', result, room=room_id)
        else:
            emit('detection_result', result)
             
        logger.info(f"Detection: {result['label']} ({result['confidence']:.2f})")

    except Exception as e:
        logger.error(f"Error in detection: {e}")
        emit('detection_error', {'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    logger.info(f"Starting server on port {port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
