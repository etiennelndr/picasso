import enum

import numpy as np
import tensorflow as tf

from ..config import Config


class Stage(enum.Enum):
    Training = "training"
    Validation = "validation"


def generator(config: Config, stage: Stage):
    keras_generator = tf.keras.preprocessing.image.ImageDataGenerator(
        rescale=1. / 255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        zoom_range=0.2
    )

    base_folder = config.base_folder / stage.value
    x_folder = base_folder / config.image_folder
    y_folder = base_folder / config.mask_folder
    assert x_folder.exists(), f"Image folder {x_folder} doesn't exist."
    assert y_folder.exists(), f"Mask folder {y_folder} doesn't exist."

    x_files = [f for f in x_folder.iterdir() if config.image_type in f.suffix]
    y_files = [f for f in y_folder.iterdir() if config.mask_type in f.suffix]
    nbr_files = len(x_files)

    steps = config.steps
    if stage is Stage.Validation:
        steps = int(steps * config.validation_split)

    i = 0
    for _ in range(steps):
        x_arrs = list()
        y_arrs = list()
        for j in range(config.batch_size):
            curr_i = i % nbr_files
            x_file = x_files[curr_i]
            y_file = y_files[curr_i]
            assert x_file.stem == y_file.stem, f"{x_file.stem} != {y_file.stem}"
            x_img = tf.keras.preprocessing.image.load_img(x_file, target_size=config.input_shape)
            y_img = tf.keras.preprocessing.image.load_img(y_file, target_size=config.output_shape)
            x_arr = tf.keras.preprocessing.image.img_to_array(x_img)
            y_arr = tf.keras.preprocessing.image.img_to_array(y_img)
            x_arr = keras_generator.random_transform(x_arr, config.seed + i)
            y_arr = keras_generator.random_transform(y_arr, config.seed + i)
            x_arr = keras_generator.standardize(x_arr)
            y_arr = keras_generator.standardize(y_arr)
            if np.all(y_arr.sum(axis=-1) == y_arr[..., 0]*3):
                y_arr = y_arr[..., 0]
                y_arr = np.expand_dims(y_arr, axis=-1)
            else:
                raise ValueError(f"Bad values in {y_arr}.")
            x_arrs.append(x_arr)
            y_arrs.append(y_arr)
            i += 1

        yield np.array(x_arrs), np.array(y_arrs)
