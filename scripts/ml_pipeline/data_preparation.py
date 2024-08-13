import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import os

def load_data():
    """Load block, delete, and normal post lists from JSON files."""
    with open('data/block.json', 'r', encoding='utf-8') as f:
        block_list = json.load(f)

    with open('data/delete_list.json', 'r', encoding='utf-8') as f:
        delete_list = json.load(f)

    with open('data/normalpost.json', 'r', encoding='utf-8') as f:
        normal_posts = json.load(f)
        
    return block_list, delete_list, normal_posts

def preprocess_data(block_list, delete_list, normal_posts):
    """Preprocess the block, delete, and normal post lists into training and test datasets."""
    # Convert lists to DataFrame
    block_df = pd.DataFrame(block_list)
    delete_df = pd.DataFrame(delete_list)
    normal_df = pd.DataFrame(normal_posts)
    
    # Add labels
    block_df['label'] = 1
    delete_df['label'] = 1
    normal_df['label'] = 0

    # Concatenate the DataFrames
    data_df = pd.concat([block_df[['post_or_comment', 'label']], delete_df[['post_or_comment', 'label']], normal_df[['title', 'label']].rename(columns={'title': 'post_or_comment'})])

    # Separate texts and labels
    texts = data_df['post_or_comment'].values
    labels = data_df['label'].values

    # Split data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)
    
    return X_train, X_test, y_train, y_test

def tokenize_and_pad(X_train, X_test):
    """Tokenize and pad the training and test data."""
    tokenizer = Tokenizer(num_words=5000, oov_token='<OOV>')
    tokenizer.fit_on_texts(X_train)

    X_train_seq = tokenizer.texts_to_sequences(X_train)
    X_test_seq = tokenizer.texts_to_sequences(X_test)

    # Pad sequences
    max_length = 100
    X_train_pad = pad_sequences(X_train_seq, maxlen=max_length, padding='post')
    X_test_pad = pad_sequences(X_test_seq, maxlen=max_length, padding='post')
    
    return tokenizer, X_train_pad, X_test_pad

def save_prepared_data(tokenizer, X_train_pad, X_test_pad, y_train, y_test):
    """Save the prepared data and tokenizer to files."""
    os.makedirs('artifacts', exist_ok=True)

    with open('artifacts/tokenizer.pkl', 'wb') as f:
        pickle.dump(tokenizer, f)

    np.save('artifacts/X_train_pad.npy', X_train_pad)
    np.save('artifacts/X_test_pad.npy', X_test_pad)
    np.save('artifacts/y_train.npy', y_train)
    np.save('artifacts/y_test.npy', y_test)

def prepare_data():
    """Main function to prepare data."""
    block_list, delete_list, normal_posts = load_data()
    X_train, X_test, y_train, y_test = preprocess_data(block_list, delete_list, normal_posts)
    tokenizer, X_train_pad, X_test_pad = tokenize_and_pad(X_train, X_test)
    save_prepared_data(tokenizer, X_train_pad, X_test_pad, y_train, y_test)

__all__ = ['load_data', 'preprocess_data', 'tokenize_and_pad', 'save_prepared_data', 'prepare_data']
