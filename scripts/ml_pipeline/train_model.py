import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, SpatialDropout1D, BatchNormalization, Bidirectional
from tensorflow.keras.callbacks import EarlyStopping, LearningRateScheduler
import tensorflow as tf
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report
import os

def load_data():
    X_train_pad = np.load('artifacts/X_train_pad.npy')
    X_test_pad = np.load('artifacts/X_test_pad.npy')
    y_train = np.load('artifacts/y_train.npy')
    y_test = np.load('artifacts/y_test.npy')
    return X_train_pad, X_test_pad, y_train, y_test

def build_model(input_length):
    model = Sequential([
        Embedding(5000, 128, input_length=input_length),
        SpatialDropout1D(0.5),
        Bidirectional(LSTM(128, dropout=0.5, recurrent_dropout=0.5, return_sequences=True)),
        Bidirectional(LSTM(64, dropout=0.5, recurrent_dropout=0.5)),
        Dense(64, activation='relu'),
        BatchNormalization(),
        Dense(1, activation='sigmoid')
    ])
    model.compile(
        loss='binary_crossentropy', 
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0005),
        metrics=['accuracy']
    )
    return model

def scheduler(epoch, lr):
    return lr * tf.math.exp(-0.05).numpy() if epoch >= 5 else lr

def augment_data(X_train_pad, y_train):
    noise = np.random.normal(0, 0.1, X_train_pad.shape)
    return X_train_pad.astype(float) + noise, y_train

def check_label_distribution(y_train):
    from collections import Counter
    distribution = Counter(y_train)
    print("Label distribution:", distribution)

def train_model():
    X_train_pad, X_test_pad, y_train, y_test = load_data()
    X_train_pad, y_train = augment_data(X_train_pad, y_train)
    check_label_distribution(y_train)

    model = build_model(X_train_pad.shape[1])
    class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
    class_weight_dict = dict(enumerate(class_weights))

    lr_scheduler = LearningRateScheduler(scheduler)
    early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

    history = model.fit(
        X_train_pad, y_train,
        epochs=20,
        batch_size=64,
        validation_split=0.2,
        class_weight=class_weight_dict,
        callbacks=[early_stopping, lr_scheduler]
    )

    loss, accuracy = model.evaluate(X_test_pad, y_test)
    print(f'Test accuracy: {accuracy:.4f}')

    y_pred = (model.predict(X_test_pad) > 0.5).astype(int).flatten()
    print(classification_report(y_test, y_pred))

    os.makedirs('models', exist_ok=True)
    model.save('models/text_classification_model.keras')
    print("Model training and saving completed.")

if __name__ == "__main__":
    train_model()
