"""Optional LSTM training hook. TensorFlow is deliberately optional."""
def train_lstm(*args, **kwargs):
    try:
        import tensorflow as tf
    except ImportError:
        return {"status": "skipped", "reason": "TensorFlow is optional and not installed"}
    return {"status": "available", "framework": tf.__name__}
