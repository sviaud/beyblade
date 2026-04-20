"""Client minimaliste pour l'API REST WordPress.

Utilise uniquement la stdlib (urllib) pour éviter les dépendances.
"""
import base64
import json
import os
import time
import urllib.parse
import urllib.request
import urllib.error


class WPClient:
    def __init__(self, base_url, user, app_password):
        self.base_url = base_url.rstrip('/')
        auth_raw = f"{user}:{app_password}".encode('utf-8')
        self.auth_header = f"Basic {base64.b64encode(auth_raw).decode('ascii')}"

    @classmethod
    def from_env(cls, env_path='config.env'):
        env = {}
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                k, _, v = line.partition('=')
                env[k.strip()] = v.strip().strip('"').strip("'")
        return cls(
            base_url=env['WP_BASE_URL'],
            user=env['WP_USER'],
            app_password=env['WP_APP_PASSWORD'],
        )

    def _request(self, method, path, params=None, data=None, retries=3):
        url = f"{self.base_url}/wp-json{path}"
        if params:
            url += '?' + urllib.parse.urlencode(params)
        headers = {
            'Authorization': self.auth_header,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) pistoletnerf-refonte/1.0',
        }
        body = json.dumps(data).encode('utf-8') if data is not None else None

        # Custom opener that follows 307/308 redirects for POST
        class SmartRedirectHandler(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, hdrs, newurl):
                m = req.get_method()
                if code in (307, 308) and m in ('POST', 'PUT', 'PATCH'):
                    newreq = urllib.request.Request(
                        newurl, data=req.data, headers=dict(req.header_items()), method=m
                    )
                    return newreq
                return super().redirect_request(req, fp, code, msg, hdrs, newurl)

        opener = urllib.request.build_opener(SmartRedirectHandler)
        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        delay = 2
        last_err = None
        for attempt in range(retries):
            try:
                with opener.open(req, timeout=30) as resp:
                    return json.loads(resp.read().decode('utf-8'))
            except urllib.error.HTTPError as e:
                if e.code in (401, 403):
                    raise RuntimeError(f"Auth failed ({e.code}) — check credentials") from e
                if e.code in (409, 422):
                    body_err = e.read().decode('utf-8', errors='replace')
                    raise RuntimeError(f"Validation error {e.code}: {body_err}") from e
                last_err = e
                if attempt < retries - 1:
                    time.sleep(delay)
                    delay *= 2
            except Exception as e:
                last_err = e
                if attempt < retries - 1:
                    time.sleep(delay)
                    delay *= 2
        raise RuntimeError(f"Request failed after {retries} retries: {last_err}")

    def get(self, path, params=None):
        return self._request('GET', path, params=params)

    def post(self, path, data):
        return self._request('POST', path, data=data)

    def get_all_posts(self, per_page=100, context='edit'):
        return self.get('/wp/v2/posts', params={'per_page': per_page, 'context': context})

    def get_post(self, post_id, context='edit'):
        return self.get(f'/wp/v2/posts/{post_id}', params={'context': context})

    def update_post(self, post_id, fields):
        return self.post(f'/wp/v2/posts/{post_id}', fields)

    def get_media(self, media_id):
        return self.get(f'/wp/v2/media/{media_id}')
