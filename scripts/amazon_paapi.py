"""Wrapper minimal pour Amazon Product Advertising API 5.0 (PA-API 5).

Marketplace : amazon.fr (region eu-west-1, host webservices.amazon.fr)
Authentication : AWS SigV4 (implémentation pure stdlib, sans dépendance externe).

Doc officielle :
- https://webservices.amazon.com/paapi5/documentation/quick-start/using-rest.html
- https://webservices.amazon.com/paapi5/documentation/get-items.html

Usage :
    from amazon_paapi import get_items
    result = get_items(['B0C2HP6XCM', 'B005U8KMJM'])
    for item in result['ItemsResult']['Items']:
        print(item['ASIN'], item.get('ItemInfo', {}).get('Title', {}).get('DisplayValue'))
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import hmac
import json
import os
import urllib.error
import urllib.request
from pathlib import Path


# ============ Config (lue depuis config.env si présent) ============

def _load_env() -> dict:
    """Charge config.env (KEY=VALUE par ligne, # = commentaire)."""
    env = {}
    cfg = Path(__file__).resolve().parent.parent / 'config.env'
    if not cfg.exists():
        return env
    for line in cfg.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


_ENV = _load_env()

ACCESS_KEY = os.environ.get('AMAZON_PAAPI_ACCESS_KEY') or _ENV.get('AMAZON_PAAPI_ACCESS_KEY')
SECRET_KEY = os.environ.get('AMAZON_PAAPI_SECRET_KEY') or _ENV.get('AMAZON_PAAPI_SECRET_KEY')
PARTNER_TAG = os.environ.get('AMAZON_PAAPI_PARTNER_TAG') or _ENV.get('AMAZON_PAAPI_PARTNER_TAG', 'beyblade0a-21')
HOST = os.environ.get('AMAZON_PAAPI_HOST') or _ENV.get('AMAZON_PAAPI_HOST', 'webservices.amazon.fr')
REGION = os.environ.get('AMAZON_PAAPI_REGION') or _ENV.get('AMAZON_PAAPI_REGION', 'eu-west-1')
MARKETPLACE = os.environ.get('AMAZON_PAAPI_MARKETPLACE') or _ENV.get('AMAZON_PAAPI_MARKETPLACE', 'www.amazon.fr')

SERVICE = 'ProductAdvertisingAPI'
ALGORITHM = 'AWS4-HMAC-SHA256'


# ============ AWS SigV4 signature ============

def _sha256_hex(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.sha256(data).hexdigest()


def _hmac_sha256(key: bytes, msg: str) -> bytes:
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()


def _signing_key(secret: str, date_stamp: str, region: str, service: str) -> bytes:
    """Derive a signing key per AWS Signature V4 spec."""
    k_date = _hmac_sha256(('AWS4' + secret).encode('utf-8'), date_stamp)
    k_region = _hmac_sha256(k_date, region)
    k_service = _hmac_sha256(k_region, service)
    return _hmac_sha256(k_service, 'aws4_request')


def _sign_request(payload: dict, target: str) -> tuple[dict, bytes]:
    """Build signed headers + body for a PA-API call.

    Returns (headers_dict, body_bytes).
    """
    if not ACCESS_KEY or not SECRET_KEY:
        raise RuntimeError("AMAZON_PAAPI_ACCESS_KEY / SECRET_KEY non configurés (voir config.env)")

    body = json.dumps(payload, separators=(',', ':')).encode('utf-8')

    now = _dt.datetime.now(tz=_dt.timezone.utc)
    amz_date = now.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = now.strftime('%Y%m%d')

    # Headers à signer (l'ordre alphabétique est important)
    canonical_headers = (
        f"content-encoding:amz-1.0\n"
        f"content-type:application/json; charset=utf-8\n"
        f"host:{HOST}\n"
        f"x-amz-date:{amz_date}\n"
        f"x-amz-target:{target}\n"
    )
    signed_headers = 'content-encoding;content-type;host;x-amz-date;x-amz-target'

    canonical_request = (
        f"POST\n"
        f"/paapi5/getitems\n"
        f"\n"  # query string vide
        f"{canonical_headers}\n"
        f"{signed_headers}\n"
        f"{_sha256_hex(body)}"
    )

    credential_scope = f"{date_stamp}/{REGION}/{SERVICE}/aws4_request"
    string_to_sign = (
        f"{ALGORITHM}\n"
        f"{amz_date}\n"
        f"{credential_scope}\n"
        f"{_sha256_hex(canonical_request)}"
    )

    signing_key = _signing_key(SECRET_KEY, date_stamp, REGION, SERVICE)
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

    authorization = (
        f"{ALGORITHM} "
        f"Credential={ACCESS_KEY}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, "
        f"Signature={signature}"
    )

    headers = {
        'Content-Encoding': 'amz-1.0',
        'Content-Type': 'application/json; charset=utf-8',
        'Host': HOST,
        'X-Amz-Date': amz_date,
        'X-Amz-Target': target,
        'Authorization': authorization,
    }
    return headers, body


# ============ API endpoint ============

DEFAULT_RESOURCES = [
    'Images.Primary.Large',
    'Images.Variants.Large',
    'ItemInfo.Title',
    'ItemInfo.Features',
    'ItemInfo.ByLineInfo',
    'ItemInfo.ProductInfo',
    'Offers.Listings.Price',
    'Offers.Listings.Availability.Type',
    'CustomerReviews.Count',
    'CustomerReviews.StarRating',
]


def get_items(asins: list[str], resources: list[str] | None = None) -> dict:
    """Appel PA-API GetItems pour une liste d'ASINs (max 10 par requête).

    Returns the parsed JSON response. Raise on HTTP error.
    """
    if not asins:
        raise ValueError("asins est vide")
    if len(asins) > 10:
        raise ValueError(f"max 10 ASINs par requête (reçu {len(asins)})")

    payload = {
        'ItemIds': asins,
        'Resources': resources or DEFAULT_RESOURCES,
        'PartnerTag': PARTNER_TAG,
        'PartnerType': 'Associates',
        'Marketplace': MARKETPLACE,
    }
    target = 'com.amazon.paapi5.v1.ProductAdvertisingAPIv1.GetItems'
    headers, body = _sign_request(payload, target)

    url = f'https://{HOST}/paapi5/getitems'
    req = urllib.request.Request(url, data=body, method='POST')
    for k, v in headers.items():
        req.add_header(k, v)

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body_resp = e.read().decode('utf-8', errors='replace')
        raise RuntimeError(f"PA-API HTTP {e.code}: {body_resp}") from e


def get_items_chunked(asins: list[str], resources: list[str] | None = None) -> list[dict]:
    """Like get_items but supports >10 ASINs by chunking. Returns flattened list of items."""
    items = []
    errors = []
    for i in range(0, len(asins), 10):
        chunk = asins[i:i+10]
        try:
            r = get_items(chunk, resources)
            if 'ItemsResult' in r and 'Items' in r['ItemsResult']:
                items.extend(r['ItemsResult']['Items'])
            if 'Errors' in r:
                errors.extend(r['Errors'])
        except Exception as e:
            errors.append({'Code': 'RequestFailed', 'Message': str(e), 'ASINs': chunk})
    return {'Items': items, 'Errors': errors}


# ============ Helpers d'extraction (depuis la réponse JSON) ============

def extract_images(item: dict) -> list[str]:
    """Retourne toutes les URLs d'images Large d'un item (primary + variants)."""
    urls = []
    images = item.get('Images', {})
    primary = images.get('Primary', {}).get('Large', {}).get('URL')
    if primary:
        urls.append(primary)
    for variant in images.get('Variants', []):
        large = variant.get('Large', {}).get('URL')
        if large and large not in urls:
            urls.append(large)
    return urls


def extract_price(item: dict) -> dict | None:
    """Retourne {amount, currency, display} ou None si pas en stock."""
    listings = item.get('Offers', {}).get('Listings', [])
    if not listings:
        return None
    p = listings[0].get('Price', {})
    return {
        'amount': p.get('Amount'),
        'currency': p.get('Currency'),
        'display': p.get('DisplayAmount'),
    }


def extract_reviews(item: dict) -> dict | None:
    """Retourne {count, star_rating} ou None si pas dispo."""
    reviews = item.get('CustomerReviews', {})
    count = reviews.get('Count')
    star = reviews.get('StarRating', {}).get('Value')
    if count is None and star is None:
        return None
    return {'count': count, 'star_rating': star}


# ============ CLI / debug ============

if __name__ == '__main__':
    import sys
    asins = sys.argv[1:] or ['B0C2HP6XCM']  # default : Dran Sword
    print(f"Fetching {len(asins)} ASIN(s) from {HOST}...\n")
    try:
        result = get_items(asins)
        for item in result.get('ItemsResult', {}).get('Items', []):
            asin = item['ASIN']
            title = item.get('ItemInfo', {}).get('Title', {}).get('DisplayValue', '?')
            images = extract_images(item)
            price = extract_price(item)
            reviews = extract_reviews(item)
            print(f"ASIN {asin}: {title}")
            print(f"  Images : {len(images)} found")
            for u in images:
                print(f"    - {u}")
            print(f"  Price  : {price['display'] if price else 'unavailable'}")
            print(f"  Reviews: {reviews if reviews else 'unavailable'}")
            print()
        if result.get('Errors'):
            print("Errors:", json.dumps(result['Errors'], indent=2))
    except Exception as e:
        print(f"FAILED: {e}", file=sys.stderr)
        sys.exit(1)
