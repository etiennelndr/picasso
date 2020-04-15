import flask


app = flask.Flask(__name__)


@app.route("/camera.en")
def english_version():
    print("switching_to_english_version")
    return flask.render_template("camera.en.html")

@app.route('/camera.fr')
def french_version():
    print("switching_to_french_version")
    return flask.render_template("camera.fr.html")
