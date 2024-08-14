import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, SpatialDropout1D, BatchNormalization, Bidirectional
from tensorflow.keras.callbacks import EarlyStopping, LearningRateScheduler
import tensorflow as tf
import os
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report

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
        SpatialDropout1D(0.5),  # Increased dropout to further reduce overfitting
        Bidirectional(LSTM(128, dropout=0.5, recurrent_dropout=0.5, return_sequences=True)),
        Bidirectional(LSTM(64, dropout=0.5, recurrent_dropout=0.5)),
        Dense(64, activation='relu'),  # Added Dense layer with ReLU activation
        BatchNormalization(),  # Added BatchNormalization after Dense layer
        Dense(1, activation='sigmoid')
    ])
    
    # Compile model with a lower initial learning rate
    model.compile(
        loss='binary_crossentropy', 
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0005),  # Adjust learning rate here
        metrics=['accuracy']
    )
    return model

def scheduler(epoch, lr):
    """Learning rate scheduler function."""
    if epoch < 5:
        return float(lr)
    else:
        # Calculate new learning rate with a slower decay rate
        new_lr = lr * tf.math.exp(-0.05)
        # Convert to float
        return float(new_lr.numpy())

def augment_data(X_train_pad, y_train):
    """Apply a simple form of data augmentation by adding Gaussian noise to the input data."""
    X_train_pad = X_train_pad.astype(float)
    noise_std_dev = 0.1
    noise = np.random.normal(0, noise_std_dev, X_train_pad.shape)
    X_train_augmented = X_train_pad + noise
    return X_train_augmented, y_train

def check_label_distribution(y_train):
    """Check and print label distribution to identify any imbalance issues."""
    from collections import Counter
    distribution = Counter(y_train)
    print("Label distribution:", distribution)

def train_model():
    """Load data, build model, train and save the model."""
    X_train_pad, X_test_pad, y_train, y_test = load_data()
    X_train_pad, y_train = augment_data(X_train_pad, y_train)
    check_label_distribution(y_train)

    model = build_model(X_train_pad.shape[1])
    
    # Compute class weights
    class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
    class_weight_dict = dict(enumerate(class_weights))

    # Define callbacks
    lr_scheduler = LearningRateScheduler(scheduler)
    early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

    # Train the model
    history = model.fit(
        X_train_pad, y_train,
        epochs=20,
        batch_size=64,
        validation_split=0.2,
        class_weight=class_weight_dict,
        callbacks=[early_stopping, lr_scheduler]
    )

    # Evaluate the model
    loss, accuracy = model.evaluate(X_test_pad, y_test)
    print(f'Test accuracy: {accuracy:.4f}')

    # Predict and evaluate classification report
    y_pred = (model.predict(X_test_pad) > 0.5).astype(int).flatten()
    print(classification_report(y_test, y_pred))

    # Save the model
    os.makedirs('models', exist_ok=True)
    model.save('models/text_classification_model.keras')
    print("Model training and saving completed.")

if __name__ == "__main__":
    train_model()
