import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import os

def load_json_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def load_data():
    block_list = load_json_file('data/block_list.json')
    delete_list = load_json_file('data/delete_list.json')
    normal_posts = load_json_file('data/normal_posts.json')
    return block_list, delete_list, normal_posts

def preprocess_data(block_list, delete_list, normal_posts):
    block_df = pd.DataFrame(block_list)
    delete_df = pd.DataFrame(delete_list)
    normal_df = pd.DataFrame(normal_posts)

    # Check necessary columns
    required_columns = {
        'block_df': 'post_or_comment',
        'delete_df': 'post_or_comment',
        'normal_df': 'title'
    }
    for df_name, column in required_columns.items():
        df = locals()[df_name]
        if column not in df.columns:
            raise KeyError(f"'{column}' column is missing in {df_name}.")

    # Assign labels and combine DataFrames
    block_df['label'] = 1
    delete_df['label'] = 1
    normal_df['label'] = 0
    data_df = pd.concat([
        block_df[['post_or_comment', 'label']],
        delete_df[['post_or_comment', 'label']],
        normal_df[['title', 'label']]
    ], ignore_index=True)

    data_df.rename(columns={'title': 'post_or_comment'}, inplace=True)
    data_df['post_or_comment'] = data_df['post_or_comment'].astype(str)

    texts = data_df['post_or_comment'].values
    labels = data_df['label'].values

    return train_test_split(texts, labels, test_size=0.2, random_state=42)

def tokenize_and_pad(X_train, X_test):
    tokenizer = Tokenizer(num_words=5000, oov_token='<OOV>')
    tokenizer.fit_on_texts(X_train)
    
    X_train_pad = pad_sequences(tokenizer.texts_to_sequences(X_train), maxlen=100, padding='post')
    X_test_pad = pad_sequences(tokenizer.texts_to_sequences(X_test), maxlen=100, padding='post')
    
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
    block_list, delete_list, normal_posts = load_data()
    X_train, X_test, y_train, y_test = preprocess_data(block_list, delete_list, normal_posts)
    tokenizer, X_train_pad, X_test_pad = tokenize_and_pad(X_train, X_test)
    save_prepared_data(tokenizer, X_train_pad, X_test_pad, y_train, y_test)

if __name__ == "__main__":
    prepare_data()
