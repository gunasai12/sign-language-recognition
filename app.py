from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import os
import json
import base64
import numpy as np
from PIL import Image
import io
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
def process_frame(frame_data):
    try:
        # Convert base64 image to numpy array
        img_data = base64.b64decode(frame_data.split(',')[1])
        img = Image.open(io.BytesIO(img_data))
        img = img.resize((224, 224))  # Resize to model input size
        img_array = np.array(img)
        
        # Normalize the image
        img_array = img_array.astype('float32') / 255.0
        
        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        # Make prediction
        predictions = model.predict(img_array)
        predicted_class_index = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_index])
        
        # Get the class label
        predicted_class = class_names[predicted_class_index]
        
        return {
            'label': predicted_class,
            'confidence': confidence
        }
    except Exception as e:
        logger.error(f"Error processing frame: {str(e)}")
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

        # Process frame
        result = process_frame(data['image'])
        if result is None:
            logger.error("Frame processing failed")
            emit('detection_error', {'error': 'Frame processing failed'})
            return

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
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting server on port {port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
