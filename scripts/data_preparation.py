import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import os

def load_data():
    with open('data/block_list.json', 'r', encoding='utf-8') as f:
        block_list = json.load(f)

    with open('data/delete_list.json', 'r', encoding='utf-8') as f:
        delete_list = json.load(f)
        
    return block_list, delete_list

def preprocess_data(block_list, delete_list):
    # 차단 및 삭제 목록 데이터를 DataFrame으로 변환
    block_df = pd.DataFrame(block_list)
    delete_df = pd.DataFrame(delete_list)

    # 필요한 열 선택 및 라벨 추가
    block_df['label'] = 1
    delete_df['label'] = 1

    # 두 데이터를 합치기
    data_df = pd.concat([block_df[['post_or_comment', 'label']], delete_df[['post_or_comment', 'label']]])

    # 텍스트와 라벨 분리
    texts = data_df['post_or_comment'].values
    labels = data_df['label'].values

    # 데이터 분리
    X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)
    
    return X_train, X_test, y_train, y_test

def tokenize_and_pad(X_train, X_test):
    tokenizer = Tokenizer(num_words=5000, oov_token='<OOV>')
    tokenizer.fit_on_texts(X_train)

    X_train_seq = tokenizer.texts_to_sequences(X_train)
    X_test_seq = tokenizer.texts_to_sequences(X_test)

    # 시퀀스 패딩
    max_length = 100
    X_train_pad = pad_sequences(X_train_seq, maxlen=max_length, padding='post')
    X_test_pad = pad_sequences(X_test_seq, maxlen=max_length, padding='post')
    
    return tokenizer, X_train_pad, X_test_pad

def save_prepared_data(tokenizer, X_train_pad, X_test_pad, y_train, y_test):
    os.makedirs('artifacts', exist_ok=True)

    with open('artifacts/tokenizer.pkl', 'wb') as f:
        pickle.dump(tokenizer, f)

    np.save('artifacts/X_train_pad.npy', X_train_pad)
    np.save('artifacts/X_test_pad.npy', X_test_pad)
    np.save('artifacts/y_train.npy', y_train)
    np.save('artifacts/y_test.npy', y_test)

def prepare_data():
    block_list, delete_list = load_data()
    X_train, X_test, y_train, y_test = preprocess_data(block_list, delete_list)
    tokenizer, X_train_pad, X_test_pad = tokenize_and_pad(X_train, X_test)
    save_prepared_data(tokenizer, X_train_pad, X_test_pad, y_train, y_test)

__all__ = ['load_data', 'preprocess_data', 'tokenize_and_pad', 'save_prepared_data', 'prepare_data']
