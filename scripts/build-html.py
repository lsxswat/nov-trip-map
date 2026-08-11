#!/usr/bin/env python3
"""Build final HTML from prefix + JSON data + JS logic, with images injected."""
import json, os

PREFIX = '/Users/talentclaw/.openclaw/workspace/nov-trip/nov-trip-map.html'
IMAGES = '/Users/talentclaw/.openclaw/workspace/nov-trip/poi-images.json'
OUTPUT = '/Users/talentclaw/.openclaw/workspace/nov-trip/nov-trip-map-final.html'

# Read the prefix
with open(PREFIX, 'r') as f:
    prefix = f.read()

# Read trip data
with open('/Users/talentclaw/.openclaw/workspace/nov-trip/trip-data.json', 'r') as f:
    tripData = json.load(f)

# Read images
images = {}
if os.path.exists(IMAGES):
    with open(IMAGES, 'r') as f:
        images = json.load(f)

# Inject images into POIs
injected = 0
for day in tripData:
    for poi in day['pois']:
        n = poi['name']
        if n in images and images[n]:
            poi['images'] = images[n]
            injected += 1
        elif 'images' not in poi:
            poi['images'] = []

print(f"Injected images into {injected} POIs")

# Build JS code
js_code = '''

// Pre-computed OSRM embedded routes
var embeddedRoutes = {
  2: {label:"~8 hours",coords:[[33.8847,-118.4108],[33.9150,-118.3870],[33.9630,-118.3450],[34.0500,-118.2500],[34.1200,-118.1500],[34.3100,-117.4800],[34.5200,-117.3200],[34.8800,-117.0200],[35.1800,-114.5700],[35.5000,-114.9000],[36.0100,-115.1700],[36.2300,-115.2500],[36.5000,-115.0000],[36.7200,-114.0700],[36.9100,-113.8800],[37.0000,-113.6800],[37.0500,-113.5700],[37.0500,-112.8800],[36.9900,-112.5300],[36.9150,-111.4600],[36.8790,-111.5100]]},
  3: {label:"~4.5 hours",coords:[[36.8790,-111.5100],[36.9100,-111.4300],[37.0000,-111.0500],[37.1000,-110.8500],[37.2000,-110.7000],[37.5000,-110.3000],[37.8000,-110.1000],[38.1000,-109.9500],[38.3000,-109.8000],[38.5000,-109.6000]]},
  8: {label:"~7 hours total",coords:[[37.1890,-112.9980],[37.1000,-113.5800],[36.8000,-113.9700],[36.6000,-114.0000],[36.3000,-115.0000],[36.1200,-115.1700],[35.5000,-114.9000],[34.8800,-117.0200],[34.5200,-117.3200],[34.3100,-117.4800],[34.1200,-118.1500],[34.0500,-118.2500]]},
  10: {label:"~5 hours",coords:[[34.0520,-118.2440],[34.0300,-117.2900],[34.0100,-116.5000],[33.9500,-116.4000],[33.8400,-116.3000],[33.7500,-116.1000],[33.6700,-115.9500],[33.6000,-115.8000],[33.4500,-115.7000],[33.2000,-116.0000],[32.9000,-116.6000],[32.8000,-116.9000],[32.7240,-117.1700]]}
};

// City groups
var cityGroups = [
  {name:"Los Angeles",coords:[34.0522,-118.2437],radius:0.5},
  {name:"Page, AZ",coords:[36.9147,-111.4558],radius:0.3},
  {name:"Moab, UT",coords:[38.5733,-109.5498],radius:0.3},
  {name:"Torrey, UT",coords:[38.2986,-111.4196],radius:0.2},
  {name:"Bryce Canyon",coords:[37.5930,-112.1871],radius:0.3},
  {name:"Springdale",coords:[37.1886,-112.9985],radius:0.2},
  {name:"Las Vegas",coords:[36.1146,-115.1728],radius:0.3},
  {name:"San Diego",coords:[32.7157,-117.1611],radius:0.4}
];

var routeColors = ['#84cc16','#eab308','#f97316','#ef4444','#ec4899','#a855f7','#6366f1','#3b82f6','#64748b','#14b8a6','#0ea5e9','#f43f5e'];

// Map init
var map = L.map('map').setView([35.5, -113.5], 7);
var grayscaleLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>',
  subdomains: 'abcd', maxZoom: 19
}).addTo(map);
var satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
  attribution: '&copy; <a href="https://www.esri.com/">Esri</a>', maxZoom: 19
});
var satelliteActive = false;

// Map toggle control
var toggleControl = L.control({position:'topright'});
toggleControl.onAdd = function() {
  var d = L.DomUtil.create('div', 'map-toggle-control');
  d.innerHTML = '<button class="map-toggle-btn active" id="btn-map">🗺️ Map</button><div class="map-toggle-divider"></div><button class="map-toggle-btn" id="btn-sat">🛰️ Satellite</button>';
  L.DomEvent.disableClickPropagation(d); L.DomEvent.disableScrollPropagation(d);
  return d;
};
toggleControl.addTo(map);

setTimeout(function(){
  document.getElementById('btn-map').addEventListener('click',function(){
    if(satelliteActive){ map.removeLayer(satelliteLayer); document.getElementById('map').classList.remove('satellite-active'); this.classList.add('active'); document.getElementById('btn-sat').classList.remove('active'); satelliteActive=false; }
  });
  document.getElementById('btn-sat').addEventListener('click',function(){
    if(!satelliteActive){ map.addLayer(satelliteLayer); document.getElementById('map').classList.add('satellite-active'); this.classList.add('active'); document.getElementById('btn-map').classList.remove('active'); satelliteActive=true; }
  });
},200);

// Legend
var legendControl = L.control({position:'bottomleft'});
legendControl.onAdd = function(){
  var d = L.DomUtil.create('div','map-legend');
  d.innerHTML = '<div class="legend-item"><i class="fa-solid fa-mountain" style="color:#2e7d32"></i> 观景点/徒步</div><div class="legend-item"><i class="fa-solid fa-person-hiking" style="color:#ef4444"></i> 步道</div><div class="legend-item"><i class="fa-solid fa-hotel" style="color:#1565c0"></i> 住宿</div><div class="legend-item"><i class="fa-solid fa-utensils" style="color:#e65100"></i> 美食/城市</div><div class="legend-item"><i class="fa-solid fa-tree" style="color:#84cc16"></i> 国家公园</div>';
  return d;
};
legendControl.addTo(map);

// City cluster labels
cityGroups.forEach(function(g){
  var icon = L.divIcon({className:'city-cluster-marker',html:'<div class="city-cluster-inner">'+g.name+'</div>',iconSize:[0,0],iconAnchor:[0,0]});
  L.marker(g.coords,{icon:icon}).addTo(map);
});

// POI markers
var allPoiMarkers = {};
function createPoiMarker(poi, di, pi){
  var icon = L.divIcon({className:'',html:'<div style="background:'+poi.color+';width:14px;height:14px;border-radius:50%;border:2px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,0.3)"></div>',iconSize:[14,14],iconAnchor:[7,7]});
  var m = L.marker(poi.coord,{icon:icon});
  m.bindTooltip(poi.name,{className:'leaflet-tooltip-own',direction:'top',offset:[0,-8]});
  m.on('click',function(){openDetail(di,pi);});
  allPoiMarkers[di+'-'+pi]=m;
  return m;
}
tripData.forEach(function(day,di){day.pois.forEach(function(poi,pi){createPoiMarker(poi,di,pi).addTo(map);});});

// Route drawing
var routePolylines = {};
function drawStraightLine(di,coords,color){
  if(routePolylines[di]) map.removeLayer(routePolylines[di]);
  routePolylines[di]=L.polyline(coords,{color:color,weight:3,opacity:0.5,dashArray:'8,8'}).addTo(map);
}
function drawOsrmRoute(di,coords,color){
  if(coords.length<2)return;
  var cs=coords.map(function(c){return c[1]+','+c[0];}).join(';');
  fetch('https://router.project-osrm.org/route/v1/driving/'+cs+'?overview=full&geometries=geojson').then(function(r){return r.json();}).then(function(data){
    if(data.code==='Ok'&&data.routes&&data.routes[0]){
      var latlngs=data.routes[0].geometry.coordinates.map(function(c){return[c[1],c[0]];});
      if(routePolylines[di])map.removeLayer(routePolylines[di]);
      routePolylines[di]=L.polyline(latlngs,{color:color,weight:4,opacity:0.7}).addTo(map);
    }else drawStraightLine(di,coords,color);
  }).catch(function(){
    if(embeddedRoutes[di+1]){var e=embeddedRoutes[di+1].coords;if(routePolylines[di])map.removeLayer(routePolylines[di]);routePolylines[di]=L.polyline(e,{color:color,weight:4,opacity:0.7}).addTo(map);}
    else drawStraightLine(di,coords,color);
  });
}
tripData.forEach(function(day,di){if(day.routeCoords&&day.routeCoords.length>=2)drawOsrmRoute(di,day.routeCoords,routeColors[di]);});

// Weather
var weatherCache={};
function fetchWeather(di,lat,lng,ds){
  var k=di+'-'+ds;if(weatherCache[k])return renderWeather(di,weatherCache[k]);
  fetch('https://api.open-meteo.com/v1/forecast?latitude='+lat+'&longitude='+lng+'&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,weathercode&timezone=America%2FLos_Angeles&forecast_days=16').then(function(r){return r.json();}).then(function(d){
    if(d.daily){var idx=-1;for(var i=0;i<d.daily.time.length;i++){if(d.daily.time[i]===ds){idx=i;break;}}
    if(idx>=0){var w={high:d.daily.temperature_2m_max[idx],low:d.daily.temperature_2m_min[idx],precip:d.daily.precipitation_probability_max[idx],code:d.daily.weathercode[idx]};weatherCache[k]=w;renderWeather(di,w);}}
  }).catch(function(){});
}
function getWeatherEmoji(code){if(code<=1)return'\\u2600\\ufe0f';if(code<=3)return'\\u26c5';if(code<=48)return'\\u2601\\ufe0f';if(code<=57)return'\\ud83c\\udf27\\ufe0f';if(code<=67)return'\\ud83c\\udf28\\ufe0f';if(code<=77)return'\\u2744\\ufe0f';if(code<=82)return'\\ud83c\\udf27\\ufe0f';if(code<=86)return'\\ud83c\\udf28\\ufe0f';return'\\u26c8\\ufe0f';}
function renderWeather(di,w){var el=document.getElementById('weather-day-'+di);if(!el)return;var h=Math.round(w.high),l=Math.round(w.low),p=w.precip;var hf=Math.round(h*9/5+32),lf=Math.round(l*9/5+32);el.innerHTML=getWeatherEmoji(w.code)+' '+hf+'\\u00b0F / '+lf+'\\u00b0F \\u00b7 \\ud83d\\udca7 '+p+'% precip';}

// Sidebar
var activeDay=0;
function renderSidebar(){
  var c=document.getElementById('sidebar-content'),h='';
  tripData.forEach(function(day,di){
    var a=(di===activeDay),cc=a?'':' collapsed',ph='';
    day.pois.forEach(function(poi,pi){ph+='<li class="sidebar-poi-item" onclick="event.stopPropagation();focusPoi('+di+','+pi+')"><span class="poi-dot" style="background-color:'+poi.color+'"></span><i class="fa-solid '+poi.icon+'" style="color:'+poi.color+';width:14px;text-align:center;font-size:11px"></i><span class="poi-name-text">'+poi.name+'<span class="poi-arrow">\\u2192</span></span></li>';});
    var cp='';day.pois.forEach(function(poi,pi){cp+='<span class="collapsed-poi-name">'+poi.name+'</span>';if(pi<day.pois.length-1)cp+=' \\u00b7 ';});
    var wds=['2026-11-11','2026-11-12','2026-11-13','2026-11-14','2026-11-15','2026-11-16','2026-11-17','2026-11-18','2026-11-19','2026-11-20','2026-11-21','2026-11-22'];
    var sh='';if(day.sunlightData){sh='<div class="sunlight-bar"><div style="display:flex;justify-content:space-between;font-size:11px;color:#64748B;margin-bottom:2px;"><span>'+day.sunlightData.sunrise+' \\u2191</span><span>'+day.sunlightData.sunset+' \\u2193</span></div><div class="sunlight-gradient" style="background:linear-gradient(to right, #4A90D9, #F5D742, #6B5B95);"></div></div>';}
    h+='<div class="day-card'+cc+'" onclick="toggleDay('+di+')"><div class="day-header">'+day.dateStr+'</div><div class="day-title">'+day.title+'</div>'+(a?'<ul class="day-pois">'+ph+'</ul>':'<div class="collapsed-pois">'+cp+'</div>')+'<div class="driving-info"><i class="fa-solid fa-car" style="color:#64748b;font-size:12px"></i> '+day.drivingInfo+'</div><div class="stay-info"><i class="fa-solid fa-moon" style="color:#64748b;font-size:12px"></i> '+day.stay+'</div>'+sh+'<div class="weather-info" id="weather-day-'+di+'">Loading weather...</div></div>';
  });
  c.innerHTML=h;
  tripData.forEach(function(day,di){var wd=wds[di]||'2026-11-11',wc=day.pois[0]?day.pois[0].coord:[34,-118];fetchWeather(di,wc[0],wc[1],wd);});
}

function toggleDay(di){if(activeDay===di){focusDay(di);return;}activeDay=di;renderSidebar();focusDay(di);var sb=document.getElementById('sidebar');if(window.innerWidth<=768){sb.classList.remove('mobile-collapsed');sb.classList.add('mobile-expanded');}setTimeout(function(){var cards=document.querySelectorAll('.day-card');if(cards[di])cards[di].scrollIntoView({behavior:'smooth',block:'nearest'});},100);}
function focusDay(di){var day=tripData[di];if(!day)return;var pcs=day.pois.map(function(p){return p.coord;});var acs=(day.routeCoords&&day.routeCoords.length>0)?day.routeCoords:pcs;if(acs.length>0)map.fitBounds(L.latLngBounds(acs),{padding:[50,50],maxZoom:12});}
function focusPoi(di,pi){var poi=tripData[di].pois[pi];if(!poi)return;activeDay=di;renderSidebar();map.setView(poi.coord,14,{animate:true});openDetail(di,pi);setTimeout(function(){var cards=document.querySelectorAll('.day-card');if(cards[di])cards[di].scrollIntoView({behavior:'smooth',block:'nearest'});},100);}

// Detail panel
var currentDetailDay=-1,currentDetailPoi=-1;
function carouselGo(idx){var pics=document.querySelectorAll('.detail-carousel img'),dots=document.querySelectorAll('.carousel-dot');pics.forEach(function(p,i){p.classList.toggle('active',i===idx);});dots.forEach(function(d,i){d.classList.toggle('active',i===idx);});}
function carouselPrev(){var pics=document.querySelectorAll('.detail-carousel img'),ci=0;pics.forEach(function(p,i){if(p.classList.contains('active'))ci=i;});carouselGo((ci-1+pics.length)%pics.length);}
function carouselNext(){var pics=document.querySelectorAll('.detail-carousel img'),ci=0;pics.forEach(function(p,i){if(p.classList.contains('active'))ci=i;});carouselGo((ci+1)%pics.length);}
function toggleNoteInput(){var el=document.getElementById('note-input-container');el.style.display=(el.style.display==='none')?'flex':'none';}
function saveNote(key){var val=document.getElementById('note-textarea').value;if(val.trim())localStorage.setItem(key,val);else localStorage.removeItem(key);openDetail(currentDetailDay,currentDetailPoi);}
function deleteNote(key){localStorage.removeItem(key);openDetail(currentDetailDay,currentDetailPoi);}
function fsOpen(src){document.getElementById('fullscreen-img').src=src;document.getElementById('fullscreen-overlay').style.display='flex';}

function openDetail(di,pi){
  currentDetailDay=di;currentDetailPoi=pi;
  var day=tripData[di],poi=day.pois[pi];
  var overlay=document.getElementById('detail-overlay'),content=document.getElementById('detail-content');
  
  var ih='';
  if(poi.images&&poi.images.length>0){
    ih='<div class="detail-carousel">';
    poi.images.forEach(function(img,ii){ih+='<img src="'+img+'" alt="'+poi.name+'" class="'+(ii===0?'active':'')+'" onclick="fsOpen(\\''+img+'\\')"'+IMG_ATTRS+'>';});
    if(poi.images.length>1){
      ih+='<button class="carousel-nav carousel-prev" onclick="event.stopPropagation();carouselPrev()"><i class="fa-solid fa-chevron-left"></i></button>';
      ih+='<button class="carousel-nav carousel-next" onclick="event.stopPropagation();carouselNext()"><i class="fa-solid fa-chevron-right"></i></button>';
      ih+='<div class="carousel-dots">';
      poi.images.forEach(function(_,ii){ih+='<button class="carousel-dot'+(ii===0?' active':'')+'" onclick="event.stopPropagation();carouselGo('+ii+')"></button>';});
      ih+='</div>';
    }
    ih+='</div>';
  }
  
  var dh='';if(poi.desc)dh='<div class="detail-section description-section"><h4><i class="fa-solid fa-circle-info"></i> 景点介绍</h4><p>'+poi.desc+'</p></div>';
  var th='';if(poi.tips)th='<div class="detail-section tips-section"><h4><i class="fa-solid fa-lightbulb"></i> 实用贴士</h4><p>'+poi.tips.replace(/\\\\n/g,'<br>')+'</p></div>';
  var wh='';if(poi.wildlife)wh='<div class="detail-section wildlife-section"><h4><i class="fa-solid fa-paw"></i> 野生动物</h4><p>'+poi.wildlife+'</p></div>';
  
  var nk='note-'+di+'-'+pi,sn=localStorage.getItem(nk)||'',nsh='';
  if(sn&&sn.trim())nsh='<div class="note-display" id="note-display"><span class="note-text-wrapper">'+sn+'</span><button class="note-delete-btn" onclick="deleteNote(\\''+nk+'\\')"><i class="fa-solid fa-trash-can"></i></button></div>';
  
  content.innerHTML=ih+'<div class="detail-body"><div class="detail-day-indicator">'+day.dateStr+'</div><div class="detail-title-container"><i class="fa-solid '+poi.icon+'" style="color:'+poi.color+'"></i><h2>'+poi.name+'</h2></div>'+dh+th+wh+'<div class="detail-actions"><a class="detail-gmaps-btn" href="https://www.google.com/maps/search/?api=1&query='+encodeURIComponent(poi.name+','+poi.coord[0]+','+poi.coord[1])+'" target="_blank"><i class="fa-solid fa-map-location-dot"></i> 在 Google Maps 中打开</a><button class="detail-note-btn" onclick="toggleNoteInput()"><i class="fa-solid fa-note-sticky"></i> '+(sn?'编辑笔记':'添加笔记')+'</button></div>'+nsh+'<div class="note-input-container" id="note-input-container" style="display:none"><textarea id="note-textarea" placeholder="在此添加笔记...">'+sn+'</textarea><button class="note-save-btn" onclick="saveNote(\\''+nk+'\\')">保存笔记</button></div></div>';
  
  overlay.style.display='block';setTimeout(function(){overlay.classList.add('open');},10);
}

function closeDetail(){var o=document.getElementById('detail-overlay');o.classList.remove('open');setTimeout(function(){o.style.display='none';},250);}
document.getElementById('detail-close-btn').addEventListener('click',closeDetail);
document.getElementById('detail-overlay').addEventListener('click',function(e){if(e.target===this)closeDetail();});
document.getElementById('fullscreen-close-btn').addEventListener('click',function(){document.getElementById('fullscreen-overlay').style.display='none';});
document.getElementById('fullscreen-overlay').addEventListener('click',function(e){if(e.target===this)this.style.display='none';});

// Sidebar title reset
document.getElementById('sidebar-title').addEventListener('click',function(){map.fitBounds([[32.5,-118.5],[39.0,-109.0]],{padding:[50,50]});activeDay=0;renderSidebar();});

// Init
renderSidebar();
var allBounds=[];tripData.forEach(function(d){if(d.routeCoords)allBounds=allBounds.concat(d.routeCoords);d.pois.forEach(function(p){allBounds.push(p.coord);});});
if(allBounds.length>0)map.fitBounds(L.latLngBounds(allBounds),{padding:[30,30]});

// Mobile drag handle
(function(){var sb=document.getElementById('sidebar'),h=document.getElementById('sidebar-drag-handle');if(!h)return;var sy=0,sh=0;h.addEventListener('touchstart',function(e){sy=e.touches[0].clientY;sh=sb.offsetHeight;sb.classList.add('dragging');});h.addEventListener('touchmove',function(e){var dy=sy-e.touches[0].clientY;var nh=Math.max(32,Math.min(90,(sh+dy)/window.innerHeight*100));sb.style.height=nh+'vh';});h.addEventListener('touchend',function(){sb.classList.remove('dragging');var hh=sb.offsetHeight/window.innerHeight*100;if(hh>45){sb.classList.remove('mobile-collapsed');sb.classList.add('mobile-expanded');sb.style.height='60vh';}else if(hh<25){sb.classList.add('mobile-collapsed');sb.classList.remove('mobile-expanded');sb.style.height='32vh';}});})();
'''

# Assemble
trip_json = json.dumps(tripData, ensure_ascii=False)
final_html = prefix + '\nvar tripData = ' + trip_json + ';' + js_code + '\n</script>\n</body>\n</html>\n'

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(final_html)

size = os.path.getsize(OUTPUT)
print(f"Final HTML: {OUTPUT} ({size} bytes, {size/1024:.1f} KB)")

# Also write to the working path
import shutil
shutil.copy(OUTPUT, '/Users/talentclaw/.openclaw/workspace/nov-trip/nov-trip-map.html')
shutil.copy(OUTPUT, '/Users/talentclaw/.openclaw/workspace/nov-trip/index.html')
print("Copied to nov-trip-map.html and index.html")
