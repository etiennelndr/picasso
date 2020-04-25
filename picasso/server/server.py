import flask


app = flask.Flask(__name__)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

LANGUAGES = {
    "en": "english",
    "fr": "french"
}


@app.after_request
def after_request(response: flask.Response):
    # Sometimes, web browsers store all files in the cache. In order to avoid
    # this behaviour, change the HTTP header with the following instructions.
    response.headers["Cache-Control"] = "no-cache, no-store," \
                                        "must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route('/camera/<language>')
def camera(language: str):
    if language not in LANGUAGES:
        flask.abort(404, f"Unsupported language: {language}.")

    return flask.render_template(f"camera.{language}.html", cache_timeout=0)
