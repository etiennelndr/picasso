import flask


app = flask.Flask(__name__)

LANGUAGES = {
    "en": "english",
    "fr": "french"
}


@app.route('/camera/<language>')
def camera(language: str):
    if language not in LANGUAGES:
        flask.abort(404, f"Unsupported language: {language}.")
    print(f"switching_to_{LANGUAGES[language]}_version")
    return flask.render_template(f"camera.{language}.html")
