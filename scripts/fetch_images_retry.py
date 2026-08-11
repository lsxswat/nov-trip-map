#!/usr/bin/env python3
"""Retry fetching images for remaining POIs with backoff."""
import json, re, subprocess, time, urllib.parse, urllib.request, sys

HTML = '/Users/talentclaw/.openclaw/workspace/nov-trip/nov-trip-map.html'
UA = {'User-Agent': 'OpenClawTripPlanner/1.0 (personal travel tool)'}

def commons_search(query, limit=8, max_retries=5):
    params = {
        'action': 'query', 'generator': 'search', 'gsrsearch': query,
        'gsrlimit': str(limit), 'gsrnamespace': '6',
        'prop': 'imageinfo', 'iiprop': 'url', 'iiurlwidth': '1280',
        'format': 'json'
    }
    url = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(params)
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode())
            results = []
            for p in data.get('query', {}).get('pages', {}).values():
                ii = p.get('imageinfo', [{}])[0]
                thumb = ii.get('thumburl') or ii.get('url')
                if thumb:
                    results.append(thumb.split('?')[0])
            return results
        except Exception as e:
            if '429' in str(e):
                wait = 15 * (attempt + 1)
                print(f'    429, waiting {wait}s...')
                time.sleep(wait)
            else:
                print(f'    error: {e}')
                time.sleep(5)
    return []

def verify_url(url):
    try:
        r = subprocess.run(['curl', '-sI', '-o', '/dev/null', '-w', '%{http_code}', '--max-time', '20', '-L', url],
                           capture_output=True, text=True, timeout=30)
        return r.stdout.strip() == '200'
    except Exception:
        return False

def main():
    html = open(HTML).read()
    m = re.search(r'var tripData = (\[.*?\]);\n', html, re.DOTALL)
    if not m:
        m = re.search(r'var tripData = (\[.*\]);', html, re.DOTALL)
    data = json.loads(m.group(1))

    # alternative query strategies per remaining POI
    strategies = {
        "Delicate Arch": ["Delicate Arch", "Delicate Arch Utah", "Delicate Arch Arches"],
        "Landscape Arch": ["Landscape Arch", "Landscape Arch Devils Garden"],
        "Sand Dune Arch": ["Sand Dune Arch", "Sand Dune Arch Arches National Park"],
        "Checkerboard Mesa": ["Checkerboard Mesa", "Checkerboard Mesa Zion National Park"],
        "Zion-Mount Carmel Tunnel": ["Zion-Mount Carmel Highway", "Zion tunnel", "Zion Mount Carmel"],
        "Canyon Overlook Trail": ["Canyon Overlook", "Zion Canyon Overlook"],
        "Torrey Pines State Reserve": ["Torrey Pines", "Torrey Pines State Natural Reserve"],
        "Balboa Park": ["Balboa Park", "Balboa Park San Diego California"],
    }

    updated = 0
    for day in data:
        for poi in day.get('pois', []):
            name = poi['name']
            if poi.get('images'):
                continue
            if name not in strategies:
                continue
            print(f'Querying: {name}')
            for q in strategies[name]:
                urls = commons_search(q)
                if not urls:
                    time.sleep(5)
                    continue
                good = []
                for u in urls:
                    if verify_url(u):
                        good.append(u)
                        if len(good) >= 2:
                            break
                    time.sleep(1)
                if good:
                    poi['images'] = good
                    updated += 1
                    print(f'  OK ({q}): {len(good)} verified')
                    break
                time.sleep(5)
            if not poi.get('images'):
                print(f'  FAILED: {name}')
            time.sleep(8)

    new_data = json.dumps(data, ensure_ascii=False)
    new_html = html.replace(m.group(1), new_data)
    open(HTML, 'w').write(new_html)

    missing = [p['name'] for d in data for p in d.get('pois', []) if not p.get('images')]
    print(f'\nDONE. Updated {updated}. Remaining without images: {len(missing)}')
    for n in missing:
        print(f'  - {n}')

if __name__ == '__main__':
    main()
