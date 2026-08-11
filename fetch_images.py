#!/usr/bin/env python3
"""Fetch Wikimedia Commons images for missing POIs in nov-trip-map.html"""
import json, re, subprocess, time, urllib.parse, urllib.request, sys

HTML = '/Users/talentclaw/.openclaw/workspace/nov-trip/nov-trip-map.html'
UA = {'User-Agent': 'OpenClawTripPlanner/1.0 (personal travel tool)'}

def commons_search(query, limit=6):
    """Search Commons for files matching query, return list of thumb URLs."""
    params = {
        'action': 'query', 'generator': 'search', 'gsrsearch': query,
        'gsrlimit': str(limit), 'gsrnamespace': '6',
        'prop': 'imageinfo', 'iiprop': 'url', 'iiurlwidth': '1280',
        'format': 'json'
    }
    url = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode())
    results = []
    pages = data.get('query', {}).get('pages', {})
    for p in pages.values():
        ii = p.get('imageinfo', [{}])[0]
        thumb = ii.get('thumburl') or ii.get('url')
        if thumb:
            # strip tracking query params
            clean = thumb.split('?')[0]
            results.append(clean)
    return results

def verify_url(url):
    """Return True if URL returns 200."""
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

    queries = {
        "Park Avenue (Arches)": "Park Avenue Arches National Park",
        "Balanced Rock": "Balanced Rock Arches National Park",
        "Windows Section": "Windows Arches National Park Turret Arch",
        "Double Arch": "Double Arch Arches National Park",
        "Delicate Arch": "Delicate Arch Arches National Park",
        "Landscape Arch": "Landscape Arch Arches National Park",
        "Sand Dune Arch": "Sand Dune Arch Arches",
        "Skyline Arch": "Skyline Arch Arches",
        "Inspiration Point": "Inspiration Point Bryce Canyon",
        "Bryce Point": "Bryce Point Bryce Canyon",
        "Navajo Loop & Queen's Garden": "Navajo Loop Queen's Garden Bryce Canyon",
        "Checkerboard Mesa": "Checkerboard Mesa Zion",
        "Zion-Mount Carmel Tunnel": "Zion Mount Carmel Highway tunnel",
        "Canyon Overlook Trail": "Canyon Overlook Trail Zion",
        "The Narrows (Riverside Walk)": "Zion Narrows Riverside Walk",
        "Scout Lookout (Optional)": "Scout Lookout Angels Landing Zion",
        "Las Vegas Sphere": "Sphere Las Vegas",
        "Downtown LA": "Downtown Los Angeles skyline",
        "Little Italy, San Diego": "Little Italy San Diego India Street",
        "La Jolla Cove": "La Jolla Cove",
        "Torrey Pines State Reserve": "Torrey Pines State Reserve",
        "Balboa Park": "Balboa Park San Diego",
        "Hotel del Coronado": "Hotel del Coronado",
        "Coronado Beach": "Coronado Beach",
        "Cabrillo National Monument": "Cabrillo National Monument",
        "USS Midway Museum": "USS Midway Museum San Diego",
    }

    # fallback: verify existing fallback image too
    updated = 0
    for day in data:
        for poi in day.get('pois', []):
            name = poi['name']
            if poi.get('images'):
                continue
            if name not in queries:
                print(f'  SKIP (no query): {name}')
                continue
            q = queries[name]
            print(f'  Querying: {name} -> "{q}"')
            urls = []
            for attempt_q in [q, name, q + ' filetype:bitmap']:
                try:
                    urls = commons_search(attempt_q)
                except Exception as e:
                    print(f'    API error: {e}')
                    urls = []
                if urls:
                    break
                time.sleep(3)
            # verify each candidate
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
                print(f'    OK: {len(good)} images verified')
            else:
                print(f'    FAILED: no verified image for {name}')
            time.sleep(3)  # rate limit

    # write back
    new_data = json.dumps(data, ensure_ascii=False)
    new_html = html.replace(m.group(1), new_data)
    open(HTML, 'w').write(new_html)
    print(f'\nDONE. Updated {updated} POIs with verified images.')
    # count remaining
    missing = [p['name'] for d in data for p in d.get('pois', []) if not p.get('images')]
    print(f'Remaining without images: {len(missing)}')
    for n in missing:
        print(f'  - {n}')

if __name__ == '__main__':
    main()
