
from flask import Flask
from .routes import bp

app = Flask(__name__)
app.register_blueprint(bp)

@app.route("/")
def hello() -> str:
    return "Hello, world!"
