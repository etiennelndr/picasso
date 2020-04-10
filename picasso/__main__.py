from tensorflow.keras.metrics import binary_accuracy

from .utils.losses import dice_loss
from .utils.metrics import dice_coef
from .models.unet import unet


if __name__ == '__main__':
    metrics = [
        dice_coef,
        binary_accuracy
    ]
    input_shape = (512, 512, 3)
    base_kernel = 16
    kernel_size = (3, 3)
    model = unet(input_shape, base_kernel, kernel_size, metrics=metrics, loss=dice_loss)
