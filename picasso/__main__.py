import pathlib

import tensorflow as tf

from .config import Config
from .models.unet import unet
from .processing.preprocessing import generator
from .processing.preprocessing import Stage


if __name__ == '__main__':
    print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))

    config = Config(pathlib.Path("data/conf.yaml"))
    input_shape = config.input_shape
    base_kernel = config.get_property("base_kernel", int)
    kernel_size = config.get_property("kernel_size", tuple)
    metrics = config.metrics
    loss = config.loss

    model = unet(input_shape, base_kernel, kernel_size, metrics=metrics, loss=loss, print_summary=False)

    for i in range(config.epochs):
        print(f"Epoch {i}/{config.epochs}")
        training_generator = generator(config, Stage.Training)
        validation_generator = generator(config, Stage.Validation)

        model.fit(
            x=training_generator,
            steps_per_epoch=config.steps,
            validation_data=validation_generator,
            validation_steps=int(config.steps * config.validation_split)
        )

        model.save(f"unet_{i}_{config.epochs}.h5", include_optimizer=False, save_format="h5")

    model.save("unet.h5", include_optimizer=False, save_format="h5")
