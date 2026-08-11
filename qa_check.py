#!/usr/bin/env python3
"""Full QA: verify every POI has desc>200, tips>100, images, and all image URLs return 200."""
import json, re, subprocess, sys

HTML = '/Users/talentclaw/.openclaw/workspace/nov-trip/nov-trip-map.html'

def verify_url(url):
    try:
        r = subprocess.run(['curl', '-sI', '-o', '/dev/null', '-w', '%{http_code}', '--max-time', '20', '-L', url],
                           capture_output=True, text=True, timeout=30)
        return r.stdout.strip()
    except Exception:
        return 'ERR'

def cjk_len(s):
    return len(re.findall(r'[\u4e00-\u9fff]', s))

def main():
    html = open(HTML).read()
    m = re.search(r'var tripData = (\[.*?\]);\n', html, re.DOTALL)
    if not m:
        m = re.search(r'var tripData = (\[.*\]);', html, re.DOTALL)
    data = json.loads(m.group(1))

    total = 0
    desc_fail = []
    tips_fail = []
    img_fail = []
    url_fail = []
    wildlife_count = 0
    total_urls = 0

    for day in data:
        for poi in day.get('pois', []):
            total += 1
            if cjk_len(poi.get('desc', '')) < 200:
                desc_fail.append(poi['name'])
            if cjk_len(poi.get('tips', '')) < 100:
                tips_fail.append(poi['name'])
            if poi.get('wildlife'):
                wildlife_count += 1
            imgs = poi.get('images', [])
            if not imgs:
                img_fail.append(poi['name'])
            for u in imgs:
                total_urls += 1
                code = verify_url(u)
                if code != '200':
                    url_fail.append((poi['name'], u, code))

    print(f'POI total: {total}')
    print(f'wildlife sections: {wildlife_count}')
    print(f'desc <200 CJK chars: {len(desc_fail)}')
    for n in desc_fail: print(f'  - {n}')
    print(f'tips <100 CJK chars: {len(tips_fail)}')
    for n in tips_fail: print(f'  - {n}')
    print(f'POIs with no images: {len(img_fail)}')
    for n in img_fail: print(f'  - {n}')
    print(f'Image URLs total: {total_urls}')
    print(f'URLs not returning 200: {len(url_fail)}')
    for n, u, c in url_fail:
        print(f'  - {n}: HTTP {c} {u[:100]}')

    ok = not (desc_fail or tips_fail or img_fail or url_fail)
    print(f'\nQA RESULT: {"PASS ✅" if ok else "FAIL ❌"}')

if __name__ == '__main__':
    main()
