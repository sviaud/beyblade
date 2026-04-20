"""Extraction et upload des images Amazon via Chrome + WP REST API."""
import json
import os
import re
import time
import urllib.request
import urllib.error
import base64


# JavaScript to extract all product images from an Amazon.fr product page
EXTRACT_IMAGES_JS = r"""
(function() {
    var results = { title: '', images: [], asin: '' };

    // Get title
    var titleEl = document.getElementById('productTitle');
    if (titleEl) results.title = titleEl.textContent.trim();

    // Get ASIN
    var asinEl = document.querySelector('[data-asin]');
    if (asinEl) results.asin = asinEl.getAttribute('data-asin');
    if (!results.asin) {
        var m = window.location.href.match(/\/dp\/([A-Z0-9]{10})/);
        if (m) results.asin = m[1];
    }

    // Method 1: Extract from colorImages JS object (most reliable)
    var scripts = document.querySelectorAll('script');
    for (var i = 0; i < scripts.length; i++) {
        var text = scripts[i].textContent;
        if (text.indexOf('colorImages') > -1) {
            var match = text.match(/'colorImages':\s*\{[^}]*'initial':\s*(\[[\s\S]*?\])\s*\}/);
            if (match) {
                try {
                    var imgs = JSON.parse(match[1]);
                    imgs.forEach(function(img) {
                        if (img.hiRes) results.images.push(img.hiRes);
                        else if (img.large) results.images.push(img.large);
                    });
                } catch(e) {}
            }
        }
    }

    // Method 2: data-old-hires + dynamic image data
    if (results.images.length === 0) {
        var mainImg = document.querySelector('#landingImage, #imgTagWrapperId img');
        if (mainImg) {
            var hires = mainImg.getAttribute('data-old-hires');
            if (hires) results.images.push(hires);
            // Parse data-a-dynamic-image
            var dynData = mainImg.getAttribute('data-a-dynamic-image');
            if (dynData) {
                try {
                    var dynObj = JSON.parse(dynData);
                    var urls = Object.keys(dynObj);
                    // Sort by resolution (largest first)
                    urls.sort(function(a, b) {
                        return (dynObj[b][0] * dynObj[b][1]) - (dynObj[a][0] * dynObj[a][1]);
                    });
                    urls.forEach(function(u) { results.images.push(u); });
                } catch(e) {}
            }
        }
    }

    // Method 3: Gallery thumbnails → large versions
    if (results.images.length === 0) {
        document.querySelectorAll('#altImages img, .imageThumbnail img').forEach(function(img) {
            var src = img.src || '';
            if (src.indexOf('media-amazon') > -1 && src.indexOf('play-button') === -1) {
                // Convert thumbnail to SL1500
                var large = src.replace(/\._[A-Z0-9,_]+_\./, '._AC_SL1500_.');
                results.images.push(large);
            }
        });
    }

    // Deduplicate
    results.images = results.images.filter(function(v, i, a) { return a.indexOf(v) === i; });

    // Filter out video thumbnails and non-product images
    results.images = results.images.filter(function(url) {
        return url.indexOf('play-button') === -1 &&
               url.indexOf('video') === -1 &&
               url.indexOf('sprite') === -1;
    });

    return JSON.stringify(results);
})();
"""


def download_image(url, dest_path):
    """Télécharge une image depuis une URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Referer': 'https://www.amazon.fr/',
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
    with open(dest_path, 'wb') as f:
        f.write(data)
    return len(data)


def upload_to_wordpress(client, image_path, filename, alt_text='', caption=''):
    """Upload une image sur WordPress via l'API REST multipart."""
    with open(image_path, 'rb') as f:
        image_data = f.read()

    # Detect content type
    ext = os.path.splitext(filename)[1].lower()
    content_types = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp', '.gif': 'image/gif'}
    content_type = content_types.get(ext, 'image/jpeg')

    boundary = '----WPUpload' + str(int(time.time()))

    body_parts = []
    # File part
    body_parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\nContent-Type: {content_type}\r\n\r\n'.encode())
    body_parts.append(image_data)
    body_parts.append(b'\r\n')

    # Alt text part
    if alt_text:
        body_parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="alt_text"\r\n\r\n{alt_text}\r\n'.encode())

    # Caption part
    if caption:
        body_parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="caption"\r\n\r\n{caption}\r\n'.encode())

    body_parts.append(f'--{boundary}--\r\n'.encode())
    body = b''.join(body_parts)

    url = f'{client.base_url}/wp-json/wp/v2/media'
    req = urllib.request.Request(url, data=body, method='POST')
    req.add_header('Authorization', client.auth_header)
    req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
    req.add_header('User-Agent', 'Mozilla/5.0 pistoletnerf-refonte/1.0')

    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read().decode('utf-8'))

    return {
        'id': result['id'],
        'url': result['source_url'],
        'alt': alt_text,
    }
