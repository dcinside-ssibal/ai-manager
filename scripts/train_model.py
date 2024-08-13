import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, SpatialDropout1D
from tensorflow.keras.callbacks import EarlyStopping
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
        SpatialDropout1D(0.2),
        LSTM(100, dropout=0.2, recurrent_dropout=0.2),
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

def train_model():
    X_train_pad, X_test_pad, y_train, y_test = load_data()

    # 모델 구축
    model = build_model(X_train_pad.shape[1])

    # 모델 학습
    early_stopping = EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

    history = model.fit(X_train_pad, y_train, epochs=10, batch_size=64, validation_split=0.2, callbacks=[early_stopping])

    # 모델 평가
    loss, accuracy = model.evaluate(X_test_pad, y_test)
    print(f'테스트 정확도: {accuracy}')

    # 모델 저장
    os.makedirs('models', exist_ok=True)
    model.save('models/text_classification_model.h5')
    print("모델 학습과 저장이 완료되었습니다.")
