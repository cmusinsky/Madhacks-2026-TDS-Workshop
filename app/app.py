from flask import Flask, request, render_template_string, jsonify
import os
from demo1 import demo1
from demo2 import demo2
from demo3 import demo3
from demo4 import demo4

app = Flask(__name__)

port = int(os.environ.get("PORT", 8000))
app.config["port"] = port

app.register_blueprint(demo1)
app.register_blueprint(demo2)
app.register_blueprint(demo3)
app.register_blueprint(demo4)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=port)
