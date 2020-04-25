import asyncio
import base64
import binascii
import imghdr
import pathlib
import socket
import ssl
import websockets

import click
import numpy as np
import tensorflow as tf
from PIL import Image
from tensorflow.keras.preprocessing import image as keras_img

from .config import Config
from .models.unet import unet
from .processing.preprocessing import Stage, generator
from .server.server import app


@click.group()
def main():
    pass


@main.command()
@click.option("--config", "-c", "config", type=str, default="data/conf.yaml")
@click.option("--model", "-m", "model", help="Use existing model", type=str)
@click.option("--epochs", "-e", "epochs", type=int)
@click.option("--start-at-epoch", "-sa", "start_at_epoch", type=int, default=0)
def train(config, model, epochs, start_at_epoch):
    """

    :param config:
    :param model:
    :param epochs:
    :param start_at_epoch:
    """
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
        model = unet(**config.get_properties(), print_summary=False)

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
    """

    :param config:
    :param image:
    :param model:
    :param threshold:
    """
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

    real_img_arr[result_arr[:, :, 0] > threshold * 255.0] = [
        255.0,
        255.0,
        255.0,
    ]
    keras_img.save_img(f"result_{pathlib.Path(image).stem}.png", real_img_arr)


@main.command()
@click.option("--host", "-h", "host", type=str)
@click.option("--port", "-p", "port", type=int, default="12400")
def server(host, port):
    """

    :param host:
    :param port:
    """
    if not host:
        hostname = socket.gethostname()
        host = socket.gethostbyname(hostname)

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(certfile=pathlib.Path('mycert.pem'))
    app.run(host=host, port=port, debug=True, ssl_context=ssl_context)


@main.command()
@click.option("--host", "-h", "host", type=str)
@click.option("--port", "-p", "port", type=int, default="12500")
def webserver(host, port):
    """

    :param host:
    :param port:
    """
    if not host:
        hostname = socket.gethostname()
        host = socket.gethostbyname(hostname)

    async def hello(websocket: websockets.WebSocketServerProtocol, path):
        """

        :param websocket:
        :param path:
        """
        print(f"New websocket with path {path}")
        msg = ""
        filename = "test.png"
        while msg != "STOP":
            msg = await websocket.recv()
            ctx, _msg = msg.split(",")
            _msg = _msg.encode()

            filepath = pathlib.Path(filename)
            try:
                result = base64.decodebytes(_msg)
                with open(filename, "wb") as img_file:
                    img_file.write(result)
                # If this file is not really an image, don't send it back.
                if not imghdr.what(filename):
                    raise ValueError("Invalid image.")
            except (binascii.Error, ValueError) as err:
                print(err)
            else:
                # Send back the same image without any changes.
                b64_result = base64.encodebytes(result)
                b64_result = b64_result.decode().replace("\n", "").encode()
                assert f"{ctx},{b64_result.decode()}" == msg
                await websocket.send(f"{ctx},{b64_result.decode()}")
            finally:
                # if filepath.exists():
                #    filepath.unlink()
                pass

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(certfile=pathlib.Path('mycert.pem'))
    start_server = websockets.serve(hello, host, port, ssl=ssl_context, extra_headers=(("Connection", "open"),))

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    main()
