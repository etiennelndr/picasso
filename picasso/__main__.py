import click
import pathlib

from PIL import Image
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image as keras_img

from .config import Config
from .models.unet import unet
from .processing.preprocessing import generator
from .processing.preprocessing import Stage


@click.group()
def main():
    pass


@main.command()
@click.option("--config", "-c", "config", type=str, default="data/conf.yaml")
@click.option("--model", "-m", "model", help="Use existing model", type=str)
@click.option("--epochs", "-e", "epochs", type=int)
@click.option("--start-at-epoch", "-sa", "start_at_epoch", type=int, default=0)
def train(config, model, epochs, start_at_epoch):
    config = Config(pathlib.Path(config))
    epochs = epochs or config.epochs

    if model:
        model = tf.keras.models.load_model(model)
        if not model._is_compiled:
            model.compile(
                optimizer=config.optimizer,
                loss=config.loss,
                metrics=config.metrics,
            )
    else:
        model = unet(**config.get_properties(), print_summary=False,)

    for i in range(start_at_epoch, epochs):
        print(f"Epoch {i+1}/{epochs}")
        training_generator = generator(config, Stage.Training)
        validation_generator = generator(config, Stage.Validation)

        model.fit(
            x=training_generator,
            steps_per_epoch=config.training_steps,
            validation_data=validation_generator,
            validation_steps=config.validation_steps,
        )
        model.save(f"unet_{i}_{epochs}.h5", save_format="h5")

    model.save("unet.h5", include_optimizer=False, save_format="h5")


@main.command()
@click.option("--config", "-c", "config", type=str, default="data/conf.yaml")
@click.option("--image", "-i", "image", type=str)
@click.option("--model", "-m", "model", type=str)
@click.option("--threshold", "-t", "threshold", type=float, default=0.75)
def predict(config, image, model, threshold):
    # Move this import at the top of this file?
    from .processing.preprocessing import keras_generator

    config = Config(pathlib.Path(config))

    img = keras_img.load_img(image)
    real_img_arr = keras_img.img_to_array(img)

    resized_img = img.resize(config.input_shape[:-1], Image.NEAREST)
    arr = keras_img.img_to_array(resized_img)
    arr = keras_generator.standardize(arr)
    arr = np.expand_dims(arr, axis=0)

    model = tf.keras.models.load_model(model, compile=False)
    result = model.predict(arr)
    result = result.squeeze(axis=0)

    result_img = keras_img.array_to_img(result)
    result_img = result_img.resize(img.size, Image.NEAREST)
    result_arr = keras_img.img_to_array(result_img)

    real_img_arr[result_arr[:, :, 0] > threshold*255.] = [255., 255., 255.]
    keras_img.save_img(f"result_{pathlib.Path(image).stem}.png", real_img_arr)


if __name__ == "__main__":
    main()
