from __future__ import annotations

import base64
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
OUTPUT_DIR = Path("generated")
OUTPUT_DIR.mkdir(exist_ok=True)


IMAGE_MODELS = {
    "flux",
    "turbo",
    "gptimage",
    "kontext",
    "seedream",
    "nanobanana",
    "nanobanana-pro",
}


def _build_prompt(prompt: str, negative_prompt: str) -> str:
    prompt_text = prompt.strip()
    negative = negative_prompt.strip()
    if negative:
        return f"{prompt_text}. Negative prompt: {negative}."
    return prompt_text


def _parse_size(size: str) -> tuple[int, int]:
    width, height = [int(x) for x in size.lower().split("x", 1)]
    return width, height


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/generate")
def generate_image():
    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "").strip()
    negative_prompt = data.get("negative_prompt", "")
    model = data.get("model", "flux")
    size = data.get("size", "1024x1024")
    output_format = data.get("output_format", "png")
    seed = str(data.get("seed", "")).strip()

    if not prompt:
        return jsonify({"error": "Prompt is required."}), 400
    if model not in IMAGE_MODELS:
        return jsonify({"error": f"Unsupported model: {model}"}), 400

    width, height = _parse_size(size)
    full_prompt = _build_prompt(prompt, negative_prompt)

    url = f"https://gen.pollinations.ai/image/{quote(full_prompt)}"
    params = {
        "model": model,
        "width": width,
        "height": height,
        "nologo": "true",
        "safe": "true",
    }
    if seed:
        params["seed"] = seed

    headers = {}
    api_key = os.getenv("POLLINATIONS_API_KEY", "").strip()
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        response = requests.get(url, params=params, headers=headers, timeout=120)
        response.raise_for_status()
    except requests.RequestException as exc:
        return jsonify({"error": f"Pollinations generation failed: {exc}"}), 502

    content_type = response.headers.get("Content-Type", "").split(";")[0].strip().lower()
    if not content_type.startswith("image/"):
        details = response.text[:200] if response.text else "No error details returned."
        return (
            jsonify({
                "error": "Pollinations returned a non-image response.",
                "details": details,
            }),
            502,
        )

    extension = "png" if content_type.endswith("png") else "jpg"
    if output_format == "png" and extension == "jpg":
        output_format = "jpg"

    filename = (
        f"image_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}.{output_format}"
    )
    path = OUTPUT_DIR / filename
    image_bytes = response.content
    path.write_bytes(image_bytes)

    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    return jsonify(
        {
            "filename": filename,
            "image_data": image_base64,
            "source": "pollinations",
            "mime_type": content_type,
            "message": "Generated using Pollinations.ai",
            "image_url": response.url,
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
