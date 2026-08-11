#!/bin/bash
# Script to query Wikimedia Commons for all POI images and verify them
# Output: JSON file with verified image URLs

set -e

POIS=(
  "LAX Airport|Los_Angeles_International_Airport"
  "Manhattan Beach|Manhattan_Beach_California"
  "Page, AZ|Page_Arizona"
  "Horseshoe Bend|Horseshoe_Bend_Arizona"
  "Lower Antelope Canyon|Lower_Antelope_Canyon"
  "Monument Valley|Monument_Valley"
  "Moab, UT|Moab_Utah"
  "Mesa Arch|Mesa_Arch_Canyonlands"
  "Grand View Point|Grand_View_Point_Canyonlands"
  "Green River Overlook|Green_River_Overlook_Canyonlands"
  "Park Avenue (Arches)|Park_Avenue_Arches_National_Park"
  "Balanced Rock|Balanced_Rock_Arches"
  "Windows Section|Windows_Arches_National_Park"
  "Double Arch|Double_Arch_Arches"
  "Delicate Arch|Delicate_Arch"
  "Landscape Arch|Landscape_Arch"
  "Sand Dune Arch|Sand_Dune_Arch_Arches"
  "Skyline Arch|Skyline_Arch_Arches"
  "Fruita Historic District|Fruita_Capitol_Reef"
  "Capitol Reef Petroglyphs|Capitol_Reef_Petroglyphs"
  "Hickman Bridge|Hickman_Bridge"
  "Scenic Drive (Capitol Reef)|Capitol_Reef_Scenic_Drive"
  "Sunset Point / Goosenecks|Goosenecks_Sulphur_Creek"
  "UT-12 Scenic Byway|Utah_State_Route_12"
  "Sunrise Point (Bryce)|Sunrise_Point_Bryce_Canyon"
  "Sunset Point (Bryce)|Sunset_Point_Bryce_Canyon"
  "Inspiration Point|Inspiration_Point_Bryce_Canyon"
  "Bryce Point|Bryce_Point"
  "Navajo Loop & Queen's Garden|Navajo_Loop_Bryce_Canyon"
  "Checkerboard Mesa|Checkerboard_Mesa"
  "Zion-Mount Carmel Tunnel|Zion_Mount_Carmel_Tunnel"
  "Canyon Overlook Trail|Canyon_Overlook_Zion"
  "The Narrows (Riverside Walk)|The_Narrows_Zion"
  "Scout Lookout|Scout_Lookout_Zion"
  "Las Vegas Sphere|Sphere_Las_Vegas"
  "Downtown LA|Downtown_Los_Angeles"
  "Los Angeles|Los_Angeles"
  "Joshua Tree West Entrance|Joshua_Tree_National_Park"
  "Hidden Valley|Hidden_Valley_Joshua_Tree"
  "Keys View|Keys_View_Joshua_Tree"
  "Skull Rock|Skull_Rock_Joshua_Tree"
  "Cholla Cactus Garden|Cholla_Cactus_Garden"
  "Cottonwood Spring|Cottonwood_Spring_Joshua_Tree"
  "Little Italy, San Diego|Little_Italy_San_Diego"
  "La Jolla Cove|La_Jolla_Cove"
  "Torrey Pines State Reserve|Torrey_Pines_State_Reserve"
  "Balboa Park|Balboa_Park_San_Diego"
  "Hotel del Coronado|Hotel_del_Coronado"
  "Coronado Beach|Coronado_Beach"
  "Cabrillo National Monument|Cabrillo_National_Monument"
  "USS Midway Museum|USS_Midway_Museum"
  "Fallback|Utah_landscape_desert"
)

OUTPUT_FILE="$(dirname "$0")/poi-images.json"

# Try to get 2 images per POI
echo "{" > "$OUTPUT_FILE"

FIRST=true
for POI_ENTRY in "${POIS[@]}"; do
  DISPLAY_NAME="${POI_ENTRY%%|*}"
  SEARCH_TERM="${POI_ENTRY##*|}"
  
  echo "Fetching: $DISPLAY_NAME ($SEARCH_TERM)" >&2
  
  # Query Wikimedia Commons
  RESPONSE=$(curl -s "https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch=${SEARCH_TERM}&gsrlimit=5&prop=imageinfo&iiprop=url&iiurlwidth=1200&format=json&origin=*")
  
  IMAGES="[]"
  if echo "$RESPONSE" | grep -q '"pages"'; then
    # Extract image URLs
    URLS=$(echo "$RESPONSE" | python3 -c "
import json, sys
try:
  data = json.load(sys.stdin)
  pages = data.get('query',{}).get('pages',{})
  urls = []
  for pid, page in pages.items():
    ii = page.get('imageinfo', [])
    if ii:
      thumb = ii[0].get('thumburl', '')
      url = ii[0].get('url', '')
      if thumb:
        urls.append(thumb)
    if len(urls) >= 2:
      break
  print(json.dumps(urls))
except:
  print('[]')
" 2>/dev/null)
    IMAGES="$URLS"
  fi
  
  # Verify each image URL with HEAD request
  VERIFIED="[]"
  if [ "$IMAGES" != "[]" ]; then
    VERIFIED=$(echo "$IMAGES" | python3 -c "
import json, sys, subprocess
urls = json.load(sys.stdin)
verified = []
for url in urls:
  try:
    r = subprocess.run(['curl', '-sI', '--max-time', '5', '-o', '/dev/null', '-w', '%{http_code}', url], capture_output=True, text=True, timeout=10)
    if r.stdout.strip() == '200':
      verified.append(url)
      print(f'  ✓ HTTP 200: {url[:80]}...', file=sys.stderr)
    else:
      print(f'  ✗ HTTP {r.stdout.strip()}: {url[:80]}...', file=sys.stderr)
  except Exception as e:
    print(f'  ✗ Error: {e}', file=sys.stderr)
  if len(verified) >= 2:
    break
print(json.dumps(verified))
" 2>/dev/null)
  fi
  
  if [ "$FIRST" = true ]; then
    FIRST=false
  else
    echo "," >> "$OUTPUT_FILE"
  fi
  
  # Escape the display name for JSON
  ESCAPED_NAME=$(echo "$DISPLAY_NAME" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read().strip()))")
  echo -n "  $ESCAPED_NAME: $VERIFIED" >> "$OUTPUT_FILE"
  
  echo "  → Got $(echo "$VERIFIED" | python3 -c "import json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo 0) verified images" >&2
done

echo "" >> "$OUTPUT_FILE"
echo "}" >> "$OUTPUT_FILE"

echo "Done! Output: $OUTPUT_FILE" >&2
