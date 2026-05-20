from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from analyzer import analyze_url
from news_finder import find_similar_news
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__, static_folder="../dist", static_url_path="")
CORS(app, origins=["http://localhost:5173"])


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True)
    if not data or "url" not in data:
        return jsonify({"error": "Se requiere el campo 'url' en el body JSON.", "analysis": None}), 400

    url = str(data["url"]).strip()
    if not url.startswith("http"):
        return jsonify({"error": "La URL debe comenzar con http:// o https://", "analysis": None}), 400

    result = analyze_url(url)

    if "error" in result:
        status_code = result.get("status", 500)
        return jsonify({"error": result["error"], "analysis": None}), status_code

    title = result.get("title", url)
    similar = find_similar_news(title)

    return jsonify({
        "analysis": result["analysis"],
        "similar_news": similar,
        "url_analyzed": url,
        "article_text": result.get("article_text", ""),
        "domain": result.get("domain", ""),
        "is_credible_source": result.get("is_credible_source", False),
        "error": None,
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


# Serve frontend SPA — catch-all for non-API routes
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    dist_path = os.path.join(os.path.dirname(__file__), "..", "dist")
    index_path = os.path.join(dist_path, "index.html")
    if not os.path.isfile(index_path):
        return jsonify({"error": "Frontend no construido. Ejecuta 'npm run build' en la raíz del proyecto."}), 503
    if path and os.path.isfile(os.path.join(dist_path, path)):
        return send_from_directory(dist_path, path)
    return send_from_directory(dist_path, "index.html")


if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5001))
    print(f"🔥 VERIFEX backend corriendo en http://localhost:{port}")
    app.run(port=port, debug=True)
