import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import os

def load_data():
    """JSON 파일에서 블록, 삭제 리스트 및 정상 게시글을 로드합니다."""
    def load_json_file(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    block_list = load_json_file('data/block_list.json')
    delete_list = load_json_file('data/delete_list.json')
    normal_posts = load_json_file('data/normal_posts.json')

    return block_list, delete_list, normal_posts

def preprocess_data(block_list, delete_list, normal_posts):
    """블록, 삭제 리스트, 정상 게시글을 훈련 및 테스트 데이터셋으로 전처리합니다."""
    # 리스트를 DataFrame으로 변환
    block_df = pd.DataFrame(block_list)
    delete_df = pd.DataFrame(delete_list)
    normal_df = pd.DataFrame(normal_posts)

    # 데이터 구조 확인
    print("block_df columns:", block_df.columns)
    print("delete_df columns:", delete_df.columns)
    print("normal_df columns:", normal_df.columns)

    # 컬럼명이 맞지 않는 경우 예외 처리
    if 'post_or_comment' not in block_df.columns:
        raise KeyError("'post_or_comment' 컬럼이 block_df에 없습니다.")
    if 'post_or_comment' not in delete_df.columns:
        raise KeyError("'post_or_comment' 컬럼이 delete_df에 없습니다.")
    
    # normal_df에서 적절한 필드로 변환
    if 'title' not in normal_df.columns:
        raise KeyError("'title' 컬럼이 normal_df에 없습니다.")
    
    block_df['label'] = 1
    delete_df['label'] = 1
    normal_df['label'] = 0  # 정상 게시글은 비문제적이라고 가정하고 0으로 설정

    # DataFrame 병합
    data_df = pd.concat([
        block_df[['post_or_comment', 'label']],
        delete_df[['post_or_comment', 'label']],
        normal_df[['title', 'label']]
    ], ignore_index=True)

    # 컬럼 이름을 통일
    data_df.rename(columns={'title': 'post_or_comment'}, inplace=True)

    # 'post_or_comment' 컬럼이 문자열이 아닌 경우 문자열로 변환
    data_df['post_or_comment'] = data_df['post_or_comment'].astype(str)

    # 텍스트와 라벨 분리
    texts = data_df['post_or_comment'].values
    labels = data_df['label'].values

    # 훈련 및 테스트 데이터셋으로 분리
    return train_test_split(texts, labels, test_size=0.2, random_state=42)

def tokenize_and_pad(X_train, X_test):
    """훈련 및 테스트 데이터를 토크나이즈하고 패딩합니다."""
    tokenizer = Tokenizer(num_words=5000, oov_token='<OOV>')

    # X_train이 문자열 배열인지 확인하고, 문자열로 변환
    X_train = [str(text) for text in X_train]
    X_test = [str(text) for text in X_test]
    
    tokenizer.fit_on_texts(X_train)

    X_train_seq = tokenizer.texts_to_sequences(X_train)
    X_test_seq = tokenizer.texts_to_sequences(X_test)

    # 시퀀스 패딩
    max_length = 100
    X_train_pad = pad_sequences(X_train_seq, maxlen=max_length, padding='post')
    X_test_pad = pad_sequences(X_test_seq, maxlen=max_length, padding='post')
    
    return tokenizer, X_train_pad, X_test_pad

def save_prepared_data(tokenizer, X_train_pad, X_test_pad, y_train, y_test):
    """준비된 데이터와 토크나이저를 파일로 저장합니다."""
    os.makedirs('artifacts', exist_ok=True)

    with open('artifacts/tokenizer.pkl', 'wb') as f:
        pickle.dump(tokenizer, f)

    np.save('artifacts/X_train_pad.npy', X_train_pad)
    np.save('artifacts/X_test_pad.npy', X_test_pad)
    np.save('artifacts/y_train.npy', y_train)
    np.save('artifacts/y_test.npy', y_test)

def prepare_data():
    """데이터를 준비하는 메인 함수."""
    block_list, delete_list, normal_posts = load_data()
    X_train, X_test, y_train, y_test = preprocess_data(block_list, delete_list, normal_posts)
    tokenizer, X_train_pad, X_test_pad = tokenize_and_pad(X_train, X_test)
    save_prepared_data(tokenizer, X_train_pad, X_test_pad, y_train, y_test)

__all__ = ['load_data', 'preprocess_data', 'tokenize_and_pad', 'save_prepared_data', 'prepare_data']
