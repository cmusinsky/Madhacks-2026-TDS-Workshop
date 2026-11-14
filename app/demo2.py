from flask import Blueprint, Flask, request, Response, render_template_string, jsonify
from pathlib import Path

demo2 = Blueprint("demo2", __name__)

APP_DIR = Path(__file__).resolve().parent
PREFS_DIR = APP_DIR / "preferences"

@demo2.route("/api/preferences")
def get_preferences():
    username = request.args.get("user", "alice")

    # Intentionally vulnerable to path traversal
    filename = PREFS_DIR / f"{username}"

    try:
        with open(filename, "r") as f:
            contents = f.read()

        return Response(contents, mimetype="text/plain")

    except FileNotFoundError:
        return "User not found", 404
    except IsADirectoryError:
        return "Invalid user", 400
