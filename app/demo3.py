from flask import Blueprint, Flask, request, Response, render_template_string, jsonify
from pathlib import Path

demo3 = Blueprint("demo3", __name__)

# This is just an endpoint that makes a javascript button you can click to create an alert
@demo3.route("/csp-demo")
def csp_demo():
    return """
    <html>
    <head>
        <title>CSP Demo</title>
    </head>
    <body style="font-family: sans-serif; padding: 50px">
        <h1>JavaScript Security Demo</h1>
        <p>Click the button below:</p>

        <button onclick="alert('JavaScript executed!')">
            Run JavaScript
        </button>
    </body>
    </html>
    """
