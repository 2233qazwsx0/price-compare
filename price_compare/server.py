import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, send_from_directory, request, jsonify
from price_compare.engine import PriceCompareEngine

app = Flask(__name__, static_folder="../web", static_url_path="")
engine = PriceCompareEngine()


@app.route("/")
def index():
    return send_from_directory("../web", "index.html")


@app.route("/api/search", methods=["POST"])
def search():
    data = request.get_json() or {}
    keyword = data.get("keyword", "").strip()
    platforms = data.get("platforms")
    max_items = data.get("max_items", 20)

    if not keyword:
        return jsonify({"error": "请输入搜索关键词"}), 400

    platform_map = {"jd": "京东", "taobao": "淘宝", "pdd": "拼多多"}
    selected = [platform_map[p] for p in platforms] if platforms else None

    eng = PriceCompareEngine(platforms=selected)
    result = eng.search(keyword, max_items_per_platform=max_items)

    return jsonify({
        "keyword": result["keyword"],
        "raw_count": result["raw_count"],
        "cleaned_count": result["cleaned_count"],
        "products": [p.to_dict() for p in result["products"]],
        "comparison": result["comparison"],
        "chart_data": result["chart_data"],
        "statistics": result["statistics"],
    })


@app.route("/api/demo", methods=["GET"])
def demo():
    demo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "web", "demo_data.json")
    demo_path = os.path.normpath(demo_path)
    if os.path.exists(demo_path):
        with open(demo_path, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    return jsonify({"error": "Demo data not found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
