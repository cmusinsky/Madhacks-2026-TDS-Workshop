import json
import logging
from datetime import datetime, timezone

from flask import Blueprint, request, jsonify, render_template_string

demo4 = Blueprint("demo4", __name__)

logger = logging.getLogger("browser-inspector")
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)

logger.propagate = False


HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Security and Privacy Party Tricks Browser Inspector</title>

<style>
    :root {
        color-scheme: dark;
    }

    * {
        box-sizing: border-box;
    }

    body {
        background: #0b1020;
        color: #e2e8f0;
        font-family: system-ui, sans-serif;
        max-width: 1100px;
        margin: 0 auto;
        padding: 30px 20px;
    }

    h1 {
        color: #38bdf8;
        font-size: 2.3rem;
        margin-bottom: 8px;
    }

    h2.section-title {
        color: #e2e8f0;
        margin: 32px 0 10px;
        font-size: 1.5rem;
    }

    .subtitle {
        color: #94a3b8;
        margin-bottom: 24px;
    }

    .notice {
        background: #172554;
        border: 1px solid #3b82f6;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 24px;
    }

    .notice p {
        margin-bottom: 0;
    }

    .grid {
        display: grid;
        grid-template-columns: repeat(
            auto-fit, minmax(min(100%, 320px), 1fr)
        );
        gap: 20px;
    }

    .card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        min-width: 0;
    }

    .card h2 {
        color: #7dd3fc;
        margin-top: 0;
        font-size: 1.2rem;
        border-bottom: 1px solid #334155;
        padding-bottom: 12px;
    }

    .field {
        display: flex;
        justify-content: space-between;
        gap: 15px;
        padding: 9px 0;
        border-bottom: 1px solid #334155;
        font-size: 0.9rem;
    }

    .field:last-child {
        border-bottom: none;
    }

    .field-name {
        color: #94a3b8;
        flex: 0 0 42%;
    }

    .field-value {
        color: #f8fafc;
        text-align: right;
        overflow-wrap: anywhere;
    }

    .status {
        margin: 20px 0;
        padding: 12px 16px;
        border-radius: 8px;
        background: #334155;
    }

    .success {
        color: #4ade80;
    }

    .error {
        color: #f87171;
    }

    .wide {
        grid-column: 1 / -1;
    }

    .fingerprint {
        font-family: monospace;
        color: #facc15;
        overflow-wrap: anywhere;
        font-size: 1rem;
    }

    .section-label {
        display: inline-block;
        font-size: 0.75rem;
        font-weight: bold;
        padding: 5px 10px;
        border-radius: 6px;
        margin-bottom: 10px;
    }

    .server-label {
        background: #164e63;
        color: #67e8f9;
    }

    .javascript-label {
        background: #713f12;
        color: #fde68a;
    }

    .explanation {
        color: #94a3b8;
        font-size: 0.9rem;
        line-height: 1.6;
        margin-bottom: 20px;
    }
</style>
</head>

<body>

<h1>Security and Privacy Party Tricks Browser Inspector</h1>

<p class="subtitle">
    How much can a website learn about your computer
    without asking for permission?
</p>

<div class="notice">
    <strong>Privacy demonstration</strong>
    <p>
        This page displays information received by the server
        and information collected using JavaScript.
        When JavaScript runs, the browser information is
        transmitted to the demonstration server.
        No camera, microphone, or location permissions
        are requested.
    </p>
</div>


<!-- =============================================== -->
<!-- SERVER-SIDE INFORMATION: NO JAVASCRIPT REQUIRED -->
<!-- =============================================== -->

<h2 class="section-title">Information Received by the Server</h2>

<span class="section-label server-label">
    HTTP REQUEST - NO JAVASCRIPT REQUIRED
</span>

<p class="explanation">
    Your browser sent this information as part of its normal
    HTTP request. Flask rendered the values into this HTML
    before sending the page back to your browser.
    Disabling JavaScript does not prevent this information
    from being transmitted.
</p>

<div class="grid">

    <div class="card">
        <h2>Connection Information</h2>

        <div class="field">
            <span class="field-name">Remote IP</span>
            <span class="field-value">{{ client_ip }}</span>
        </div>

        <div class="field">
            <span class="field-name">X-Forwarded-For</span>
            <span class="field-value">{{ forwarded_for }}</span>
        </div>

        <div class="field">
            <span class="field-name">HTTP Method</span>
            <span class="field-value">{{ method }}</span>
        </div>

        <div class="field">
            <span class="field-name">Request Path</span>
            <span class="field-value">{{ path }}</span>
        </div>

        <div class="field">
            <span class="field-name">Protocol</span>
            <span class="field-value">{{ protocol }}</span>
        </div>
    </div>

    <div class="card">
        <h2>HTTP Request Headers</h2>

        {% for name, value in headers %}
        <div class="field">
            <span class="field-name">{{ name }}</span>
            <span class="field-value">{{ value }}</span>
        </div>
        {% endfor %}

        {% if not headers %}
        <p>No request headers received.</p>
        {% endif %}
    </div>

</div>


<!-- =============================================== -->
<!-- JAVASCRIPT INFORMATION                          -->
<!-- =============================================== -->

<h2 class="section-title">Information Collected by JavaScript</h2>

<span class="section-label javascript-label">
    BROWSER FINGERPRINTING - JAVASCRIPT REQUIRED
</span>

<p class="explanation">
    The following information is collected by JavaScript
    running inside your browser. Unlike the HTTP headers
    above, these details are not automatically included
    in the original request.
</p>

<div id="js-status" class="status">
    JavaScript has not executed. Browser information
    has not been collected or transmitted.
</div>

<div id="dashboard" class="grid"></div>


<script>
async function collectBrowserInfo() {
    const info = {
        "Browser": {
            "User Agent": navigator.userAgent,
            "Platform": navigator.platform,
            "Vendor": navigator.vendor,
            "Language": navigator.language,
            "Languages": navigator.languages.join(", "),
            "Cookies Enabled": navigator.cookieEnabled,
            "Do Not Track": navigator.doNotTrack
        },

        "Hardware": {
            "CPU Threads": navigator.hardwareConcurrency,
            "Approximate RAM (GB)":
                navigator.deviceMemory ?? "Unavailable",
            "Touch Points": navigator.maxTouchPoints,
            "Pixel Ratio": window.devicePixelRatio
        },

        "Display": {
            "Screen Resolution":
                screen.width + " x " + screen.height,
            "Available Resolution":
                screen.availWidth + " x " + screen.availHeight,
            "Viewport":
                innerWidth + " x " + innerHeight,
            "Color Depth": screen.colorDepth,
            "Pixel Depth": screen.pixelDepth
        },

        "Location Clues": {
            "Timezone": Intl.DateTimeFormat()
                .resolvedOptions().timeZone,
            "Timezone Offset (minutes)":
                new Date().getTimezoneOffset(),
            "Locale": Intl.DateTimeFormat()
                .resolvedOptions().locale
        },

        "Preferences": {
            "Dark Mode": matchMedia(
                "(prefers-color-scheme: dark)"
            ).matches,
            "Reduced Motion": matchMedia(
                "(prefers-reduced-motion: reduce)"
            ).matches,
            "High Contrast": matchMedia(
                "(prefers-contrast: more)"
            ).matches,
            "Forced Colors": matchMedia(
                "(forced-colors: active)"
            ).matches,
            "HDR Display": matchMedia(
                "(dynamic-range: high)"
            ).matches
        },

        "Network": {
            "Online": navigator.onLine
        }
    };

    // Network Information API
    const connection = navigator.connection;

    if (connection) {
        info["Network"]["Connection Type"] =
            connection.effectiveType;
        info["Network"]["Downlink (Mbps)"] =
            connection.downlink;
        info["Network"]["RTT (ms)"] =
            connection.rtt;
        info["Network"]["Save Data"] =
            connection.saveData;
    }

    // WebGL graphics information
    try {
        const canvas = document.createElement("canvas");
        const gl = canvas.getContext("webgl");

        if (gl) {
            const debug = gl.getExtension(
                "WEBGL_debug_renderer_info"
            );

            info["Graphics"] = {
                "Vendor": gl.getParameter(gl.VENDOR),
                "Renderer": gl.getParameter(gl.RENDERER),
                "WebGL Version": gl.getParameter(gl.VERSION),
                "Max Texture Size":
                    gl.getParameter(gl.MAX_TEXTURE_SIZE),
                "GPU Vendor": debug
                    ? gl.getParameter(
                        debug.UNMASKED_VENDOR_WEBGL
                    )
                    : "Unavailable",
                "GPU Renderer": debug
                    ? gl.getParameter(
                        debug.UNMASKED_RENDERER_WEBGL
                    )
                    : "Unavailable"
            };
        }
    } catch (error) {
        info["Graphics"] = {
            "Error": String(error)
        };
    }

    // Browser storage estimate
    if (navigator.storage?.estimate) {
        try {
            const storage = await navigator.storage.estimate();

            info["Storage"] = {
                "Quota (MB)": Math.round(
                    (storage.quota ?? 0) / 1048576
                ),
                "Used (MB)": Math.round(
                    (storage.usage ?? 0) / 1048576
                )
            };
        } catch (error) {
            info["Storage"] = {
                "Error": String(error)
            };
        }
    }

    return info;
}


function displayDashboard(info) {
    const dashboard = document.getElementById("dashboard");
    dashboard.replaceChildren();

    for (const [section, fields] of Object.entries(info)) {
        const card = document.createElement("div");
        card.className = "card";

        const heading = document.createElement("h2");
        heading.textContent = section;
        card.appendChild(heading);

        for (const [name, value] of Object.entries(fields)) {
            const row = document.createElement("div");
            row.className = "field";

            const label = document.createElement("span");
            label.className = "field-name";
            label.textContent = name;

            const val = document.createElement("span");
            val.className = "field-value";
            val.textContent = String(value ?? "Unavailable");

            row.append(label, val);
            card.appendChild(row);
        }

        dashboard.appendChild(card);
    }
}


async function calculateFingerprint(info) {
    if (!crypto.subtle) {
        return "Unavailable (requires HTTPS or localhost)";
    }

    // Use relatively stable characteristics
    const stable = {
        browser: info["Browser"],
        hardware: info["Hardware"],
        display: {
            resolution: info["Display"]["Screen Resolution"],
            colorDepth: info["Display"]["Color Depth"]
        },
        location: info["Location Clues"],
        graphics: info["Graphics"]
    };

    const bytes = new TextEncoder().encode(
        JSON.stringify(stable)
    );

    const digest = await crypto.subtle.digest(
        "SHA-256", bytes
    );

    return Array.from(new Uint8Array(digest))
        .map(b => b.toString(16).padStart(2, "0"))
        .join("");
}


async function runInspection() {
    const status = document.getElementById("js-status");

    try {
        status.textContent = "Collecting browser information...";

        const info = await collectBrowserInfo();

        displayDashboard(info);

        const fingerprint = await calculateFingerprint(info);

        info["Fingerprint"] = fingerprint;

        const card = document.createElement("div");
        card.className = "card wide";

        const heading = document.createElement("h2");
        heading.textContent = "Browser Fingerprint";

        const value = document.createElement("div");
        value.className = "fingerprint";
        value.textContent = fingerprint;

        card.append(heading, value);
        document.getElementById("dashboard").appendChild(card);

        const response = await fetch("/api/browser-info", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(info)
        });

        if (!response.ok) {
            throw new Error("HTTP " + response.status);
        }

        status.className = "status success";
        status.textContent =
            "Browser information successfully transmitted to server.";

    } catch (error) {
        status.className = "status error";
        status.textContent = "Error: " + error.message;
    }
}

runInspection();
</script>

</body>
</html>
"""


@demo4.route("/inspect")
def inspect():
    return render_template_string(
        HTML,
        headers=list(request.headers.items()),
        client_ip=request.remote_addr,
        forwarded_for=request.headers.get(
            "X-Forwarded-For", "Not set"
        ),
        method=request.method,
        path=request.path,
        protocol=request.environ.get(
            "SERVER_PROTOCOL", "Unknown"
        )
    )


@demo4.route("/api/browser-info", methods=["POST"])
def browser_info():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Expected JSON object"}), 400

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

    client_ip = request.remote_addr
    forwarded_for = request.headers.get(
        "X-Forwarded-For", "Not set"
    )

    report = [
        "",
        "=" * 80,
        "  BROWSER PRIVACY INSPECTOR - NEW VISITOR",
        "=" * 80,
        f"  Timestamp:       {timestamp}",
        f"  Connection IP:   {client_ip}",
        f"  X-Forwarded-For: {forwarded_for}",
        "-" * 80
    ]

    for section, fields in data.items():
        report.append("")
        report.append(f"  [{section.upper()}]")

        if isinstance(fields, dict):
            width = max(
                (len(str(key)) for key in fields),
                default=0
            )

            for key, value in fields.items():
                report.append(
                    f"    {str(key):<{width}} : {value}"
                )
        else:
            report.append(f"    {fields}")

    report.extend(["", "=" * 80, ""])

    logger.info("\n".join(report))

    return jsonify({"status": "received"})
