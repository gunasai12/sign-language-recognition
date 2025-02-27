import tensorflow as tf
import tensorflowjs as tfjs

# Load the model
model = tf.keras.models.load_model('../sign_language_model.h5')

# Convert and save the model for TensorFlow.js
tfjs.converters.save_keras_model(model, '../video_call_app/public/sign_language_model')
