import flask


app = flask.Flask(__name__)


@app.route("/camera")
def get_camera_stream():
    print("get_camera_stream")
    return flask.render_template("camera.html")
