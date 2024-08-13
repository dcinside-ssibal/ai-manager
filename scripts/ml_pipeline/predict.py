import pickle
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

# 전역 변수로 모델과 토크나이저를 로드
tokenizer = None
model = None

def load_resources():
    """Load tokenizer and model from files."""
    global tokenizer, model
    if tokenizer is None or model is None:
        print("Loading resources...")
        try:
            with open('artifacts/tokenizer.pkl', 'rb') as f:
                tokenizer = pickle.load(f)
            print("Tokenizer loaded successfully.")
            
            model = load_model('models/text_classification_model.h5')
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Error loading resources: {e}")
            tokenizer = None
            model = None
    return tokenizer, model

def preprocess_text(text):
    """Preprocess text for model prediction."""
    print(f"Preprocessing text: {text}")
    try:
        sequences = tokenizer.texts_to_sequences([text])
        padded_sequences = pad_sequences(sequences, maxlen=100)
        print("Text preprocessing complete.")
        return padded_sequences
    except Exception as e:
        print(f"Error preprocessing text: {e}")
        return None

def predict_text(text):
    """Predict if the given text is problematic."""
    print(f"Predicting text: {text}")
    try:
        processed_text = preprocess_text(text)
        if processed_text is not None:
            prediction = model.predict(processed_text)
            print(f"Prediction result: {prediction[0][0]}")
            return prediction[0][0] > 0.8  # 임계값을 0.8로 설정
        else:
            print("Preprocessed text is None.")
            return False
    except Exception as e:
        print(f"Error predicting text: {e}")
        return False

def predict(title):
    """Run prediction for the given title."""
    print(f"Running prediction for title: {title}")
    # Ensure resources are loaded
    load_resources()
    return predict_text(title)
