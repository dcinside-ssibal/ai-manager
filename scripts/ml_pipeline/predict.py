import pickle
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

tokenizer = None
model = None

def load_resources():
    global tokenizer, model
    if tokenizer is None or model is None:
        try:
            with open('artifacts/tokenizer.pkl', 'rb') as f:
                tokenizer = pickle.load(f)
            model = load_model('models/text_classification_model.keras')
        except (FileNotFoundError, pickle.PickleError) as e:
            print(f"Error loading resources: {e}")
            tokenizer = model = None
        except Exception as e:
            print(f"Unexpected error: {e}")
            tokenizer = model = None
    return tokenizer, model

def preprocess_text(text):
    try:
        sequences = tokenizer.texts_to_sequences([text])
        return pad_sequences(sequences, maxlen=100)
    except Exception as e:
        print(f"Error preprocessing text: {e}")
        return None

def predict_text(text):
    processed_text = preprocess_text(text)
    if processed_text is None:
        return False
    try:
        prediction = model.predict(processed_text)
        return prediction[0][0] > 0.8
    except Exception as e:
        print(f"Error during prediction: {e}")
        return False

def predict(title):
    tokenizer, model = load_resources()
    if tokenizer is None or model is None:
        print("Resources not loaded.")
        return False
    return predict_text(title)
