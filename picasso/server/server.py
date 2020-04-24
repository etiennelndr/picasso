import base64
import binascii
import imghdr
import pathlib

import quart


app = quart.Quart(__name__)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

LANGUAGES = {
    "en": "english",
    "fr": "french"
}


@app.after_request
def after_request(response: quart.Response):
    # Sometimes, web browsers store all files in the cache. In order to avoid
    # this behaviour, change the HTTP header with the following instructions.
    response.headers["Cache-Control"] = "no-cache, no-store," \
                                        "must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route('/camera/<language>')
async def camera(language: str):
    if language not in LANGUAGES:
        quart.abort(404, f"Unsupported language: {language}.")

    return await quart.render_template(f"camera.{language}.html", cache_timeout=0)


@app.websocket("/predict")
async def predict():
    print(f"New websocket with path predict")
    msg = ""
    filename = "test.png"
    while msg != "STOP":
        msg = await quart.websocket.receive()
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
            await quart.websocket.send(f"{ctx},{b64_result.decode()}")
        finally:
            if filepath.exists():
                filepath.unlink()
