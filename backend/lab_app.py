"""Intentionally vulnerable LOCAL lab application for authorized scanner demos.

Run: python lab_app.py  -> http://127.0.0.1:8000
Only bind to localhost. Never expose this app publicly.
"""

from flask import Flask, request

app = Flask(__name__)


@app.after_request
def add_weak_headers(response):
    response.headers["Server"] = "VulnerableLab/1.0"
    response.headers["X-Powered-By"] = "SecureAI-Demo-Framework"
    # Deliberately no CSP, X-Frame-Options, HSTS, nosniff or Referrer-Policy.
    return response


@app.route("/")
def index():
    query = request.args.get("q", request.args.get("secureai_probe", ""))
    response = app.response_class(
        f"""<!doctype html>
<html><head><title>SecureAI Vulnerable Lab</title></head>
<body>
<h1>Authorized Security Testing Lab</h1>
<p>This local application intentionally contains weak configurations for scanner practice.</p>
<script>
  var reflectedValue = "{query}";
  document.write("");
</script>
<ul>
  <li><a href="/error?q=demo">Error demo page</a></li>
  <li><a href="/uploads/">File uploads directory</a></li>
  <li><a href="/about">About</a></li>
</ul>
</body></html>"""
    )
    response.set_cookie("session", "lab-session-token", httponly=False, secure=False, samesite=None)
    return response


@app.route("/error")
def error_page():
    value = request.args.get("q", "demo")
    return (
        f"""<!doctype html><html><head><title>Debug Error</title></head>
<body><h1>Database error</h1>
<pre>Warning: SQL syntax near '{value}' in query: SELECT * FROM users WHERE id = '{value}'</pre>
<p><a href="/">Back to lab</a></p></body></html>""",
        500,
    )


@app.route("/uploads/")
def uploads():
    return """<!doctype html><html><head><title>Index of /uploads/</title></head>
<body><h1>Index of /uploads/</h1>
<a href="../">Parent Directory</a><br>
<a href="notes.txt">notes.txt</a><br>
<a href="backup.zip">backup.zip</a><br>
</body></html>"""


@app.route("/about")
def about():
    return "<!doctype html><html><head><title>About lab</title></head><body><h1>About this lab</h1><p>Local only.</p></body></html>"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=False, threaded=True)
