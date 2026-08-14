import joblib

def load_model(model_path):
    model = joblib.load(model_path)
    return model

def predict(model, features):
    prediction = model.predict(features)
    return prediction[0]  # Return the first prediction result
