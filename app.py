from flask import Flask, request, jsonify, send_file
import requests
import logging
from io import BytesIO
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# Faster JSON
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False

# Disable logs
logging.basicConfig(level=logging.ERROR)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# APIs
INFO_API = "https://stargamerff.qzz.io/accinfo"
BANNER_API = "http://103.138.96.154:2002/banner-image"
OUTFIT_API = "http://103.138.96.154:2002/outfit-image"

# Reuse connections = faster
session = requests.Session()

# Thread pool
executor = ThreadPoolExecutor(max_workers=20)


def fetch_info(uid, region=None):
    params = {"uid": uid}

    if region:
        params["region"] = region

    response = session.get(
        INFO_API,
        params=params,
        timeout=5
    )

    if response.status_code != 200:
        return None

    return response.json()


@app.route('/banner', methods=['GET'])
def get_banner():
    uid = request.args.get('uid')

    if not uid:
        return jsonify({"error": "Missing uid"}), 400

    region = request.args.get('region')

    try:
        data = fetch_info(uid, region)

        if not data:
            return jsonify({"error": "Failed"}), 500

        basic = data.get('basicInfo', {})
        clan = data.get('clanBasicInfo', {})

        frame = basic.get('frame', '')

        banner_url = (
            f"{BANNER_API}"
            f"?headPic={basic.get('headPic', '')}"
            f"&bannerId={basic.get('bannerId', '')}"
            f"&name={quote(str(basic.get('nickname', '')))}"
            f"&level={basic.get('level', 1)}"
            f"&guild={quote(str(clan.get('clanName', '')))}"
            f"&pinId={basic.get('pinId', '900000012')}"
            f"&celebrity={basic.get('celebrityStatus', 0)}"
            f"&primeLevel={basic.get('primeInfo', {}).get('primeLevel', 0)}"
            f"&frame={quote(str(frame))}"
        )

        response = session.get(
            banner_url,
            timeout=5
        )

        if response.status_code != 200:
            return jsonify({"error": "Failed"}), 500

        content_type = response.headers.get(
            'content-type',
            'image/png'
        )

        return send_file(
            BytesIO(response.content),
            mimetype=content_type,
            as_attachment=False
        )

    except Exception:
        return jsonify({"error": "Failed"}), 500


@app.route('/outfit', methods=['GET'])
def get_outfit():
    uid = request.args.get('uid')

    if not uid:
        return jsonify({"error": "Missing uid"}), 400

    region = request.args.get('region')

    try:
        data = fetch_info(uid, region)

        if not data:
            return jsonify({"error": "Failed"}), 500

        profile = data.get('profileInfo', {})

        avatar_id = profile.get('avatarId', '')
        clothes_list = profile.get('clothes', [])

        clothes_str = ",".join(
            [str(x).strip() for x in clothes_list]
        )

        outfit_url = (
            f"{OUTFIT_API}"
            f"?avatarId={avatar_id}"
            f"&clothes={clothes_str}"
        )

        response = session.get(
            outfit_url,
            timeout=5
        )

        if response.status_code != 200:
            return jsonify({"error": "Failed"}), 500

        content_type = response.headers.get(
            'content-type',
            'image/png'
        )

        return send_file(
            BytesIO(response.content),
            mimetype=content_type,
            as_attachment=False
        )

    except Exception:
        return jsonify({"error": "Failed"}), 500


@app.route('/banner-url', methods=['GET'])
def get_banner_url():
    uid = request.args.get('uid')

    if not uid:
        return jsonify({"error": "Missing uid"}), 400

    region = request.args.get('region')

    try:
        data = fetch_info(uid, region)

        if not data:
            return jsonify({"error": "Failed"}), 500

        basic = data.get('basicInfo', {})
        clan = data.get('clanBasicInfo', {})

        frame = basic.get('frame', '')

        banner_url = (
            f"{BANNER_API}"
            f"?headPic={basic.get('headPic', '')}"
            f"&bannerId={basic.get('bannerId', '')}"
            f"&name={quote(str(basic.get('nickname', '')))}"
            f"&level={basic.get('level', 1)}"
            f"&guild={quote(str(clan.get('clanName', '')))}"
            f"&pinId={basic.get('pinId', '900000012')}"
            f"&celebrity={basic.get('celebrityStatus', 0)}"
            f"&primeLevel={basic.get('primeInfo', {}).get('primeLevel', 0)}"
            f"&frame={quote(str(frame))}"
        )

        return jsonify({
            "url": banner_url
        })

    except Exception:
        return jsonify({"error": "Failed"}), 500


@app.route('/outfit-url', methods=['GET'])
def get_outfit_url():
    uid = request.args.get('uid')

    if not uid:
        return jsonify({"error": "Missing uid"}), 400

    region = request.args.get('region')

    try:
        data = fetch_info(uid, region)

        if not data:
            return jsonify({"error": "Failed"}), 500

        profile = data.get('profileInfo', {})

        avatar_id = profile.get('avatarId', '')
        clothes_list = profile.get('clothes', [])

        clothes_str = ",".join(
            [str(x).strip() for x in clothes_list]
        )

        outfit_url = (
            f"{OUTFIT_API}"
            f"?avatarId={avatar_id}"
            f"&clothes={clothes_str}"
        )

        return jsonify({
            "url": outfit_url
        })

    except Exception:
        return jsonify({"error": "Failed"}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok"
    }), 200


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        threaded=True,
        debug=False
    )