import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, SpatialDropout1D
from tensorflow.keras.callbacks import EarlyStopping
import os

def load_data():
    """Load the training and testing data."""
    X_train_pad = np.load('artifacts/X_train_pad.npy')
    X_test_pad = np.load('artifacts/X_test_pad.npy')
    y_train = np.load('artifacts/y_train.npy')
    y_test = np.load('artifacts/y_test.npy')
    
    return X_train_pad, X_test_pad, y_train, y_test

def build_model(input_length):
    """Build and compile the LSTM model."""
    model = Sequential([
        Embedding(5000, 128, input_length=input_length),
        SpatialDropout1D(0.2),
        LSTM(100, dropout=0.2, recurrent_dropout=0.2),
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

def train_model():
    """Load data, build model, train and save the model."""
    X_train_pad, X_test_pad, y_train, y_test = load_data()

    # Build the model
    model = build_model(X_train_pad.shape[1])

    # Train the model with early stopping
    early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

    history = model.fit(X_train_pad, y_train, epochs=10, batch_size=64, validation_split=0.2, callbacks=[early_stopping])

    # Evaluate the model
    loss, accuracy = model.evaluate(X_test_pad, y_test)
    print(f'Test accuracy: {accuracy:.4f}')

    # Save the model
    os.makedirs('models', exist_ok=True)
    model.save('models/text_classification_model.keras')
    print("Model training and saving completed.")
