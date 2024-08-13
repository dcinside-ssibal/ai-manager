import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, SpatialDropout1D, BatchNormalization, Bidirectional
from tensorflow.keras.callbacks import EarlyStopping, LearningRateScheduler
import tensorflow as tf
import os

def load_data():
    """Load the training and testing data."""
    X_train_pad = np.load('artifacts/X_train_pad.npy')
    X_test_pad = np.load('artifacts/X_test_pad.npy')
    y_train = np.load('artifacts/y_train.npy')
    y_test = np.load('artifacts/y_test.npy')
    
    return X_train_pad, X_test_pad, y_train, y_test

def build_model(input_length):
    """Build and compile the LSTM model with improved architecture and batch normalization."""
    model = Sequential([
        Embedding(5000, 128, input_length=input_length),
        SpatialDropout1D(0.3),  # Increased dropout to reduce overfitting
        Bidirectional(LSTM(128, dropout=0.3, recurrent_dropout=0.3, return_sequences=True)),
        Bidirectional(LSTM(64, dropout=0.3, recurrent_dropout=0.3)),
        Dense(64, activation='relu'),  # Added Dense layer with ReLU activation
        BatchNormalization(),  # Added BatchNormalization after Dense layer
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

def scheduler(epoch, lr):
    """Learning rate scheduler function."""
    if epoch < 3:
        return float(lr)
    else:
        # Calculate new learning rate
        new_lr = lr * tf.math.exp(-0.1)
        # Convert to float
        return float(new_lr.numpy())

def augment_data(X_train_pad, y_train):
    """Apply a simple form of data augmentation by adding Gaussian noise to the input data.
    
    Args:
        X_train_pad (numpy.ndarray): The padded training data.
        y_train (numpy.ndarray): The labels corresponding to the training data.
    
    Returns:
        Tuple[numpy.ndarray, numpy.ndarray]: Augmented training data and corresponding labels.
    """
    # Ensure that X_train_pad is of float type for noise addition
    X_train_pad = X_train_pad.astype(float)
    
    # Define the standard deviation for the Gaussian noise
    noise_std_dev = 0.1
    
    # Generate Gaussian noise
    noise = np.random.normal(0, noise_std_dev, X_train_pad.shape)
    
    # Add noise to the training data
    X_train_augmented = X_train_pad + noise
    
    return X_train_augmented, y_train

def train_model():
    """Load data, build model, train and save the model."""
    # Load the data
    X_train_pad, X_test_pad, y_train, y_test = load_data()

    # Data augmentation
    X_train_pad, y_train = augment_data(X_train_pad, y_train)

    # Build the model
    model = build_model(X_train_pad.shape[1])

    # Define callbacks
    lr_scheduler = LearningRateScheduler(scheduler)
    early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)  # Increased patience for early stopping

    # Train the model
    history = model.fit(
        X_train_pad, y_train,
        epochs=20,  # Increased epochs to allow more training time
        batch_size=64,
        validation_split=0.2,  # Use 20% of training data for validation
        callbacks=[early_stopping, lr_scheduler]  # Callbacks for early stopping and learning rate adjustment
    )

    # Evaluate the model
    loss, accuracy = model.evaluate(X_test_pad, y_test)
    print(f'Test accuracy: {accuracy:.4f}')

    # Save the model
    os.makedirs('models', exist_ok=True)
    model.save('models/text_classification_model.keras')
    print("Model training and saving completed.")

    # Optional: Plot training history
    # plot_history(history)


if __name__ == "__main__":
    train_model()
