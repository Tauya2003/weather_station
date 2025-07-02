
# Edge Device Prediction Function
import numpy as np
import tensorflow as tf
import json

class WeatherPredictor:
    def __init__(self, model_path, config_path):
        # Load TFLite model
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.scale_values = np.array(self.config['preprocessing']['scale_values'])
        self.min_values = np.array(self.config['preprocessing']['min_values'])
    
    def normalize_input(self, data):
        """Normalize input data using saved scaler parameters"""
        return (data - self.min_values) / self.scale_values
    
    def denormalize_output(self, data):
        """Denormalize output predictions"""
        # Only denormalize the first 4 features (weather targets)
        scale_subset = self.scale_values[:4]
        min_subset = self.min_values[:4]
        return (data * scale_subset) + min_subset
    
    def predict(self, weather_sequence):
        """
        Predict next day weather
        weather_sequence: array of shape (30, 6) with last 30 days of weather data
        Returns: [precipitation, avg_temp, max_temp, min_temp] for next day
        """
        # Normalize input
        normalized_input = self.normalize_input(weather_sequence)
        
        # Reshape for model input
        input_data = normalized_input.reshape(1, 30, 6).astype(np.float32)
        
        # Run prediction
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
        
        # Denormalize output
        prediction = self.denormalize_output(output_data[0])
        
        return {
            'precipitation': float(prediction[0]),
            'avg_temperature': float(prediction[1]),
            'max_temperature': float(prediction[2]),
            'min_temperature': float(prediction[3])
        }

# Example usage:
# predictor = WeatherPredictor('weather_prediction_model.tflite', 'model_config.json')
# result = predictor.predict(last_30_days_data)
