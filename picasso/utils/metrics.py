"""
Source: https://github.com/PhotoRoom/starter-challenge-data-2020
"""
import tensorflow.keras.backend as K


def dice_coeff(y_true, y_pred):
    y_true_f = K.flatten(y_true)
    y_pred = K.cast(y_pred, "float32")
    y_pred_f = K.cast(K.greater(K.flatten(y_pred), 0.5), "float32")
    intersection = y_true_f * y_pred_f
    return 2.0 * K.sum(intersection) / (K.sum(y_true_f) + K.sum(y_pred_f))
