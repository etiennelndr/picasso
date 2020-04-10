import typing

import tensorflow as tf
from tensorflow.keras import Input
from tensorflow.keras import Model
from tensorflow.keras.layers import Activation
from tensorflow.keras.layers import Concatenate
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import Layer
from tensorflow.keras.layers import MaxPooling2D
from tensorflow.keras.layers import UpSampling2D
from tensorflow.keras.losses import BinaryCrossentropy
from tensorflow.keras.losses import Loss
from tensorflow.keras.metrics import BinaryAccuracy
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.optimizers import Optimizer


def up(
    kernel: int,
    kernel_size: typing.Tuple[int, ...],
    input_layer: Layer,
    pool_size: typing.Tuple[int, ...]
) -> typing.Tuple[Layer, Layer]:
    conv = Conv2D(kernel, kernel_size, padding='same')(input_layer)
    acti = Activation(tf.nn.relu)(conv)
    conv = Conv2D(kernel, kernel_size, padding='same')(acti)
    acti = Activation(tf.nn.relu)(conv)
    return acti, MaxPooling2D(pool_size=pool_size)(acti)


def down(
    kernel: int,
    kernel_size: typing.Tuple[int, ...],
    input_layer: Layer,
    up_size: typing.Tuple[int, ...],
    conc_layer: Layer
) -> Layer:
    upsp = UpSampling2D(size=up_size)(input_layer)
    conc = Concatenate(axis=3)([upsp, conc_layer])
    conv = Conv2D(kernel, kernel_size, padding='same')(conc)
    acti9 = Activation(tf.nn.relu)(conv)
    conv = Conv2D(kernel, kernel_size, padding='same')(acti9)
    return Activation(tf.nn.relu)(conv)


def unet(
    input_shape: typing.Tuple[int, ...],
    base_kernel: int,
    kernel_size: typing.Tuple[int, ...],
    optimizer: typing.Union[None, str, Optimizer] = None,
    loss: typing.Union[None, str, Loss] = None,
    metrics: typing.Optional[typing.List] = None,
    print_summary: bool = True
) -> Model:
    """
    U-Net model for image segmentation.

    Source: https://arxiv.org/abs/1505.04597
    """
    if not optimizer:
        optimizer = Adam()
    if not loss:
        loss = BinaryCrossentropy()
    if not metrics:
        metrics = [BinaryAccuracy()]

    inputs = Input(input_shape)

    up1, max1 = up(base_kernel, kernel_size, inputs, (2, 2))
    up2, max2 = up(base_kernel*2, kernel_size, max1, (2, 2))
    up3, max3 = up(base_kernel*4, kernel_size, max2, (2, 2))
    up4, max4 = up(base_kernel*8, kernel_size, max3, (2, 2))

    conv = Conv2D(base_kernel*16, kernel_size, padding='same')(max4)
    acti = Activation(tf.nn.relu)(conv)
    conv = Conv2D(base_kernel*16, kernel_size, padding='same')(acti)
    acti = Activation(tf.nn.relu)(conv)

    down1 = down(base_kernel*8, kernel_size, acti, (2, 2), up4)
    down2 = down(base_kernel*4, kernel_size, down1, (2, 2), up3)
    down3 = down(base_kernel*2, kernel_size, down2, (2, 2), up2)
    down4 = down(base_kernel, kernel_size, down3, (2, 2), up1)

    conv10 = Conv2D(2, kernel_size, padding='same')(down4)
    acti10 = Activation(tf.nn.relu)(conv10)
    conv10 = Conv2D(1, (1, 1), padding='same')(acti10)
    acti10 = Activation(tf.nn.sigmoid)(conv10)

    model = Model(inputs=inputs, outputs=acti10)
    model.compile(optimizer=optimizer, loss=loss, metrics=metrics)

    if print_summary:
        model.summary()

    return model
