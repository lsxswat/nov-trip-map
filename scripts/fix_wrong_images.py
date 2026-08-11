#!/usr/bin/env python3
"""Fix WRONG images (content mismatch) for specific POIs with precise queries."""
import json, re, subprocess, time, urllib.parse, urllib.request

HTML = '/Users/talentclaw/.openclaw/workspace/nov-trip/nov-trip-map.html'
UA = {'User-Agent': 'OpenClawTripPlanner/1.0 (personal travel tool)'}

def commons_search(query, limit=8, max_retries=6):
    params = {
        'action': 'query', 'generator': 'search', 'gsrsearch': query,
        'gsrlimit': str(limit), 'gsrnamespace': '6',
        'prop': 'imageinfo', 'iiprop': 'url|size|mime', 'iiurlwidth': '1280',
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
                mime = ii.get('mime', '')
                if mime not in ('image/jpeg', 'image/png', 'image/webp'):
                    continue
                thumb = ii.get('thumburl') or ii.get('url')
                if thumb:
                    results.append(thumb.split('?')[0])
            return results
        except Exception as e:
            if '429' in str(e):
                wait = 20 * (attempt + 1)
                print(f'    429, waiting {wait}s...')
                time.sleep(wait)
            else:
                print(f'    error: {e}')
                time.sleep(6)
    return []

def verify_url(url):
    try:
        r = subprocess.run(['curl', '-sI', '-o', '/dev/null', '-w', '%{http_code}', '--max-time', '20', '-L', url],
                           capture_output=True, text=True, timeout=30)
        return r.stdout.strip() == '200'
    except Exception:
        return False

# POI -> list of query strategies (precise, avoids wrong matches)
fixes = {
    "Coronado Beach": ["Coronado Beach California sand", "Coronado Beach San Diego shoreline"],
    "Canyon Overlook Trail": ["Zion Canyon Overlook Trail", "Canyon Overlook Trail Zion National Park"],
    "Navajo Loop & Queen's Garden": ["Navajo Loop Bryce Canyon", "Queens Garden Trail Bryce Canyon hoodoos"],
    "Little Italy, San Diego": ["Little Italy San Diego", "India Street Little Italy San Diego"],
    "Zion-Mount Carmel Tunnel": ["Zion Mount Carmel Highway tunnel", "Zion-Mount Carmel Highway"],
    "Los Angeles": ["Los Angeles skyline", "Downtown Los Angeles skyline California"],
    "Moab, UT": ["Moab Utah downtown", "Moab Utah Main Street"],
    "Fruita Historic District": ["Fruita Capitol Reef orchard", "Fruita Schoolhouse Capitol Reef"],
    "Bryce Point": ["Bryce Point view Bryce Canyon", "Bryce Point Bryce Canyon panorama"],
    "Sunset Point (Bryce)": ["Bryce Canyon Sunset Point view", "Thor's Hammer Bryce Sunset Point"],
}

def main():
    html = open(HTML).read()
    m = re.search(r'var tripData = (\[.*?\]);', html, re.DOTALL)
    data = json.loads(m.group(1))
    fixed = 0
    for day in data:
        for poi in day.get('pois', []):
            name = poi['name']
            if name not in fixes:
                continue
            print(f'Fixing: {name}')
            for q in fixes[name]:
                urls = commons_search(q)
                if not urls:
                    time.sleep(6)
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
                    fixed += 1
                    print(f'  OK: replaced with {len(good)} verified ({q})')
                    break
                time.sleep(6)
            if not poi.get('images'):
                print(f'  FAILED: {name}')
            time.sleep(10)

    new_data = json.dumps(data, ensure_ascii=False)
    open(HTML, 'w').write(html.replace(m.group(1), new_data))
    print(f'\nDONE. Fixed {fixed} POIs.')

if __name__ == '__main__':
    main()
