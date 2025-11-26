"""
Minimal TensorFlow Keras intent classifier scaffold.

Usage:
  - Install dependencies: `pip install tensorflow` (see README notes)
  - Train: run `python -m chatbot.intent_model train` (from project root)
  - The trained model will be saved under `chatbot/intent_classifier/` and used by `chatbot.views`.

This module is intentionally small and uses TextVectorization + Embedding + GlobalAveragePooling.
For production use, expand the training data and tune hyperparameters.
"""
import os
import json
import pathlib

MODEL_DIR = pathlib.Path(__file__).parent / 'intent_classifier'
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / 'model'
LABELS_PATH = MODEL_DIR / 'labels.json'

try:
    import numpy as np
    import tensorflow as tf
    from tensorflow.keras import layers
    TF_AVAILABLE = True
except Exception:
    TF_AVAILABLE = False

from .intent_examples import INTENT_EXAMPLES

_loaded = None
_vectorize_layer = None
_labels = None


def _build_dataset():
    texts = []
    labels = []
    for intent, examples in INTENT_EXAMPLES.items():
        for t in examples:
            texts.append(t)
            labels.append(intent)
    return texts, labels


def train_model(epochs=30):
    if not TF_AVAILABLE:
        raise RuntimeError('TensorFlow not available. Install tensorflow to train the intent model.')

    texts, labels = _build_dataset()
    unique_labels = sorted(list(set(labels)))
    label_to_index = {l: i for i, l in enumerate(unique_labels)}
    y = np.array([label_to_index[l] for l in labels])

    # Simple text vectorization
    vectorize_layer = layers.TextVectorization(max_tokens=20000, output_mode='int', output_sequence_length=32)
    vectorize_layer.adapt(texts)

    X = vectorize_layer(np.array([[t] for t in texts])).numpy()

    vocab_size = len(vectorize_layer.get_vocabulary())

    model = tf.keras.Sequential([
        layers.Input(shape=(None,), dtype='int64'),
        layers.Embedding(input_dim=vocab_size, output_dim=64),
        layers.GlobalAveragePooling1D(),
        layers.Dense(64, activation='relu'),
        layers.Dense(len(unique_labels), activation='softmax')
    ])

    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.fit(X, y, epochs=epochs, verbose=2)

    # Save model and assets
    MODEL_PATH.mkdir(parents=True, exist_ok=True)
    model.save(str(MODEL_PATH), overwrite=True)

    # Save labels and vocabulary
    with open(LABELS_PATH, 'w', encoding='utf8') as f:
        json.dump(unique_labels, f)

    # Save vectorizer vocabulary
    vocab = vectorize_layer.get_vocabulary()
    with open(MODEL_DIR / 'vocab.json', 'w', encoding='utf8') as f:
        json.dump(vocab, f)

    print('Intent model trained and saved to', MODEL_PATH)


def load_model():
    global _loaded, _vectorize_layer, _labels
    if _loaded is not None:
        return _loaded
    if not TF_AVAILABLE:
        return None
    if not MODEL_PATH.exists():
        return None
    try:
        model = tf.keras.models.load_model(str(MODEL_PATH))
        # Reconstruct vectorize layer from saved vocab
        vocab_file = MODEL_DIR / 'vocab.json'
        if vocab_file.exists():
            with open(vocab_file, 'r', encoding='utf8') as f:
                vocab = json.load(f)
            _vectorize_layer = layers.TextVectorization(max_tokens=len(vocab), output_mode='int', output_sequence_length=32)
            _vectorize_layer.set_vocabulary(vocab)
        # load labels
        if LABELS_PATH.exists():
            with open(LABELS_PATH, 'r', encoding='utf8') as f:
                _labels = json.load(f)
        _loaded = model
        return model
    except Exception:
        return None


def predict_intent(text, top_k=1):
    """Return (intent, confidence) or (None, 0) if model not available."""
    model = load_model()
    if model is None or not TF_AVAILABLE:
        return None, 0.0
    if not _vectorize_layer:
        # load vectorizer via load_model side-effect
        load_model()
    try:
        x = _vectorize_layer([text])
        preds = model.predict(x)
        preds = preds[0]
        idx = int(np.argmax(preds))
        label = _labels[idx] if _labels else None
        conf = float(preds[idx])
        return label, conf
    except Exception:
        return None, 0.0


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['train'], help='Action to perform')
    parser.add_argument('--epochs', type=int, default=30)
    args = parser.parse_args()
    if args.action == 'train':
        train_model(epochs=args.epochs)
