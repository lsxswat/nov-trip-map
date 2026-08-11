#!/bin/bash
# Fetch images from Wikimedia Commons for all Utah Mighty Five POIs
# Key fix: use gsrnamespace=6 to search File namespace only, iiurlwidth=1280

POIS=(
"LAX Airport|Los_Angeles_International_Airport"
"Manhattan Beach|Manhattan_Beach_California_pier"
"Page, AZ|Page_Arizona_Lake_Powell"
"Horseshoe Bend|Horseshoe_Bend_Arizona"
"Lower Antelope Canyon|Lower_Antelope_Canyon"
"Monument Valley (Optional)|Monument_Valley"
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
"Sunset Point / Goosenecks|Capitol_Reef_Goosenecks"
"UT-12 Scenic Byway|Utah_State_Route_12"
"Sunrise Point (Bryce)|Sunrise_Point_Bryce_Canyon"
"Sunset Point (Bryce)|Sunset_Point_Bryce_Canyon"
"Inspiration Point|Inspiration_Point_Bryce_Canyon"
"Bryce Point|Bryce_Point"
"Navajo Loop & Queen's Garden|Navajo_Loop_Bryce_Canyon"
"Checkerboard Mesa|Checkerboard_Mesa_Zion"
"Zion-Mount Carmel Tunnel|Zion_Mount_Carmel_Tunnel"
"Canyon Overlook Trail|Canyon_Overlook_Zion"
"The Narrows (Riverside Walk)|The_Narrows_Zion"
"Scout Lookout (Optional)|Scout_Lookout_Zion"
"Las Vegas Sphere|Sphere_Las_Vegas"
"Downtown LA|Downtown_Los_Angeles_skyline"
"Los Angeles|Los_Angeles_cityscape"
"Joshua Tree West Entrance|Joshua_Tree_National_Park_entrance"
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
"Coronado Beach|Coronado_Beach_San_Diego"
"Cabrillo National Monument|Cabrillo_National_Monument"
"USS Midway Museum|USS_Midway_Museum"
)

OUTDIR="$(dirname "$0")"
IMGFILE="$OUTDIR/poi-images.json"

echo "{" > "$IMGFILE"

COUNT=0
TOTAL=${#POIS[@]}
SUCCESS=0

for entry in "${POIS[@]}"; do
  NAME="${entry%%|*}"
  SEARCH="${entry##*|}"
  COUNT=$((COUNT + 1))
  
  echo "[$COUNT/$TOTAL] $NAME ..." >&2
  
  # Query Wikimedia Commons - search File namespace only
  APIURL="https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch=$(python3 -c "import urllib.parse; print(urllib.parse.quote('${SEARCH}'))")&gsrnamespace=6&gsrlimit=5&prop=imageinfo&iiprop=url&iiurlwidth=1280&format=json&origin=*"
  
  RESPONSE=$(curl -s --max-time 10 "$APIURL")
  
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
      if thumb:
        urls.append(thumb)
    if len(urls) >= 2:
      break
  print(json.dumps(urls))
except Exception as e:
  print('[]')
  print(f'Error: {e}', file=sys.stderr)
" 2>/dev/null)
  
  # Verify URLs
  VERIFIED="["
  if [ "$URLS" != "[]" ]; then
    VCOUNT=0
    IFS=$'\n'
    for url in $(echo "$URLS" | python3 -c "import json,sys; [print(u) for u in json.load(sys.stdin)]" 2>/dev/null); do
      HTTPCODE=$(curl -sI --max-time 5 -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
      if [ "$HTTPCODE" = "200" ]; then
        if [ $VCOUNT -gt 0 ]; then VERIFIED="$VERIFIED,"; fi
        VERIFIED="$VERIFIED\"$url\""
        VCOUNT=$((VCOUNT + 1))
        echo "  OK: $url" | cut -c1-120 >&2
      else
        echo "  FAIL($HTTPCODE): $url" | cut -c1-120 >&2
      fi
      if [ $VCOUNT -ge 2 ]; then break; fi
    done
  fi
  VERIFIED="$VERIFIED]"
  
  if [ $COUNT -gt 1 ]; then
    echo "," >> "$IMGFILE"
  fi
  echo -n "  \"$NAME\": $VERIFIED" >> "$IMGFILE"
  
  VCNT=$(echo "$VERIFIED" | python3 -c "import json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo 0)
  if [ "$VCNT" -gt 0 ]; then SUCCESS=$((SUCCESS + 1)); fi
  
done

echo "" >> "$IMGFILE"
echo "}" >> "$IMGFILE"

echo ""
echo "=== DONE ===" >&2
echo "Total POIs: $TOTAL" >&2
echo "POIs with images: $SUCCESS" >&2
echo "Output: $IMGFILE" >&2
