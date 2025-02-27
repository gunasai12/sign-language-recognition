import tensorflow as tf
import os

# Load the Keras model
model = tf.keras.models.load_model("models/sign_language_model.keras")

# Create directory for the converted model
os.makedirs("static/model", exist_ok=True)

# Convert and save the model for TensorFlow.js
tf.saved_model.save(model, "static/model/tmp")
os.system("tensorflowjs_converter --input_format=tf_saved_model --output_format=tfjs_graph_model static/model/tmp static/model")
