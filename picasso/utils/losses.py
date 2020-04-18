"""
Source: https://github.com/PhotoRoom/starter-challenge-data-2020
"""
import tensorflow.keras.backend as K
from tensorflow.keras.losses import binary_crossentropy


def dice_loss(y_true, y_pred):
    smooth = 1.0
    y_true_f = K.flatten(y_true)
    y_pred_f = K.flatten(y_pred)
    intersection = y_true_f * y_pred_f
    score = (2.0 * K.sum(intersection) + smooth) / (
        K.sum(y_true_f) + K.sum(y_pred_f) + smooth
    )
    return 1.0 - score


def bce_dice_loss(y_true, y_pred):
    return binary_crossentropy(y_true, y_pred) + dice_loss(y_true, y_pred)


def bce_logdice_loss(y_true, y_pred):
    return binary_crossentropy(y_true, y_pred) - K.log(
        1.0 - dice_loss(y_true, y_pred)
    )


def weighted_bce_loss(y_true, y_pred, weight):
    epsilon = 1e-7
    y_pred = K.clip(y_pred, epsilon, 1.0 - epsilon)
    logit_y_pred = K.log(y_pred / (1.0 - y_pred))
    loss = weight * (
        logit_y_pred * (1.0 - y_true)
        + K.log(1.0 + K.exp(-K.abs(logit_y_pred)))
        + K.maximum(-logit_y_pred, 0.0)
    )
    return K.sum(loss) / K.sum(weight)


def weighted_dice_loss(y_true, y_pred, weight):
    smooth = 1.0
    w, m1, m2 = weight, y_true, y_pred
    intersection = m1 * m2
    score = (2.0 * K.sum(w * intersection) + smooth) / (
        K.sum(w * m1) + K.sum(w * m2) + smooth
    )
    return 1.0 - K.sum(score)


def weighted_bce_dice_loss(y_true, y_pred):
    y_true = K.cast(y_true, "float32")
    y_pred = K.cast(y_pred, "float32")
    # If we want to get same size of output, kernel size must be odd.
    averaged_mask = K.pool2d(
        y_true,
        pool_size=(50, 50),
        strides=(1, 1),
        padding="same",
        pool_mode="avg",
    )
    weight = K.ones_like(averaged_mask)
    w0 = K.sum(weight)
    weight = 5.0 * K.exp(-5.0 * K.abs(averaged_mask - 0.5))
    w1 = K.sum(weight)
    weight *= w0 / w1
    return weighted_bce_loss(y_true, y_pred, weight) + dice_loss(y_true, y_pred)
