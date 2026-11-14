from flask import Blueprint, Flask, current_app, request, render_template_string, jsonify
import os

demo1 = Blueprint("demo1", __name__)


HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>HAProxy Demo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            background: {{ '#4a1010' if penalty else '#102a1c' }};
            color: white;
            padding: 80px 20px;
        }
        h1 { font-size: 48px; }
        .box {
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 30px;
            max-width: 650px;
            margin: auto;
        }
        button {
            padding: 15px 30px;
            font-size: 20px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="box">
        {% if penalty %}
            <h1>You've Been Rate Limited!</h1>
            <p>Our security system has determined that
            you are a menace to society.</p>
            <p>Please stop abusing the refresh button.</p>
        {% else %}
            <h1>Welcome to the Hackathon!</h1>
            <p>You are currently accessing the normal backend.</p>
            <p>Try refreshing repeatedly to trigger rate limiting.</p>
        {% endif %}

        <hr>

        <p><b>Backend port:</b> {{ port }}</p>
        <p><b>Client IP:</b> {{ client_ip }}</p>
        <p><b>X-Forwarded-For:</b> {{ forwarded_for }}</p>

        <button onclick="location.reload()">Send Another Request</button>
    </div>
</body>
</html>
"""

@demo1.route("/")
def index():
    port = current_app.config["port"]
    penalty = port == 10001
    return render_template_string(
        HTML,
        penalty=penalty,
        port=port,
        client_ip=request.remote_addr,
        forwarded_for=request.headers.get("X-Forwarded-For", "Not set")
    )


@demo1.route("/health")
def health():
    return "OK", 200
