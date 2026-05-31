"""
components/map_component.py - Data pulses & animated POIs + Live Job Pins
"""

import json
import streamlit as st

_BG = "#0e1117"
_ROUTE_COLOR = "#00f3ff"
_BUILDING_COLOR = "#1a2030"

SAMPLE_POIS = [
    {"name": "Waverley Shul", "lat": -26.145, "lon": 28.045, "intensity": 0.9, "type": "religious"},
    {"name": "Toyota", "lat": -26.140, "lon": 28.050, "intensity": 0.7, "type": "commercial"},
    {"name": "Auto Ihurst", "lat": -26.138, "lon": 28.048, "intensity": 0.6, "type": "commercial"},
    {"name": "Woolworths", "lat": -26.143, "lon": 28.052, "intensity": 0.85, "type": "retail"},
    {"name": "Mezepoli", "lat": -26.142, "lon": 28.053, "intensity": 0.75, "type": "restaurant"},
    {"name": "Foschini", "lat": -26.141, "lon": 28.054, "intensity": 0.65, "type": "retail"},
    {"name": "Piza eVino", "lat": -26.144, "lon": 28.055, "intensity": 0.8, "type": "restaurant"},
    {"name": "Truworths", "lat": -26.146, "lon": 28.051, "intensity": 0.7, "type": "retail"},
    {"name": "Paul", "lat": -26.147, "lon": 28.049, "intensity": 0.6, "type": "cafe"},
    {"name": "Studio Nine", "lat": -26.148, "lon": 28.047, "intensity": 0.55, "type": "entertainment"},
    {"name": "Edgars", "lat": -26.149, "lon": 28.053, "intensity": 0.75, "type": "retail"},
    {"name": "FNB", "lat": -26.150, "lon": 28.056, "intensity": 0.8, "type": "financial"},
    {"name": "Clicks", "lat": -26.151, "lon": 28.052, "intensity": 0.65, "type": "retail"},
    {"name": "Istanbul Kebab", "lat": -26.152, "lon": 28.048, "intensity": 0.7, "type": "restaurant"},
]

POI_COLORS = {
    "religious": "#9b59b6",
    "commercial": "#3498db",
    "retail": "#e74c3c",
    "restaurant": "#e67e22",
    "cafe": "#f39c12",
    "entertainment": "#1abc9c",
    "financial": "#2ecc71",
    "default": "#95a5a6"
}

JOB_SECTOR_COLORS = {
    "IT":         "#00f3ff",
    "Banking":    "#FFD700",
    "Healthcare": "#50C878",
    "Security":   "#FF4D4D",
    "Other":      "#94a3b8",
}

JOB_SECTOR_ICONS = {
    "IT":         "monitor",
    "Banking":    "landmark",
    "Healthcare": "activity",
    "Security":   "shield",
    "Other":      "briefcase",
}


def build_map_html(
    midpoint_lat: float,
    midpoint_lon: float,
    route_geojson: dict,
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    start_name: str = "Origin",
    end_name: str = "Destination",
    pois: list = None,
    job_pins: list = None,
    
) -> str:
    maptiler_key = st.secrets.get("MAPTILER_KEY", "")
    route_json_str = json.dumps(route_geojson)
    route_json_str_escaped = route_json_str.replace("</", "<\\/")

    pois_data = pois if pois is not None else SAMPLE_POIS
    pois_json = json.dumps(pois_data)
    geocoded_jobs = [j for j in (job_pins or []) if "lat" in j and "lon" in j]
    jobs_json = json.dumps([
        {
            "lat":      j["lat"],
            "lon":      j["lon"],
            "title":    j["title"],
            "company":  j["company"],
            "location": j["location"],
            "sector":   j["sector"],
            "color":    j["color"],
            "url":      j["url"],
        }
        for j in geocoded_jobs
    ])

    start_name_js = json.dumps(start_name)
    end_name_js   = json.dumps(end_name)
    poi_colors_js = json.dumps(POI_COLORS)

    html = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="initial-scale=1,maximum-scale=1,user-scalable=no" />
  <script src="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.js"></script>
  <link href="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.css" rel="stylesheet" />
  <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html, body { background: BG_COLOR; width: 100%; height: 100%; overflow: hidden; }
    #map {
      position: absolute; inset: 0;
      -webkit-mask-image: radial-gradient(ellipse 92% 92% at 50% 50%, black 60%, transparent 100%);
      mask-image: radial-gradient(ellipse 92% 92% at 50% 50%, black 60%, transparent 100%);
    }
    .marker-label {
      background: rgba(10,14,23,0.92); border: 1px solid ROUTE_COLOR88; color: #e8eaf0;
      font-family: 'DM Mono', monospace; font-size: 11px; letter-spacing: 0.04em;
      padding: 6px 12px; border-radius: 6px; white-space: nowrap;
      backdrop-filter: blur(8px); pointer-events: none; font-weight: 500;
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    .maplibregl-popup-content {
      background: rgba(10,14,23,0.97) !important; padding: 0 !important;
      border-radius: 10px !important; box-shadow: 0 8px 32px rgba(0,0,0,0.6) !important;
      min-width: 230px; max-width: 290px;
    }
    .maplibregl-popup-tip { display: none; }
    .job-popup-inner { padding: 14px 16px 12px; }
    .job-popup-sector {
      font-size: 0.62rem; font-weight: 700; letter-spacing: 0.1em;
      text-transform: uppercase; margin-bottom: 6px;
      display: flex; align-items: center; gap: 5px;
    }
    .job-popup-title  { font-size: 0.82rem; font-weight: 700; color: #e2e8f0; line-height: 1.3; margin-bottom: 6px; }
    .job-popup-meta   { display: flex; align-items: center; gap: 5px; font-size: 0.72rem; color: #64748b; margin-bottom: 3px; }
    .job-popup-apply {
      display: flex; align-items: center; justify-content: center; gap: 5px;
      margin-top: 10px; padding: 6px 0; border-radius: 6px;
      font-size: 0.7rem; font-weight: 700; letter-spacing: 0.06em;
      text-decoration: none; transition: opacity 0.15s;
    }
    .job-popup-apply:hover { opacity: 0.8; }
    .data-pulse { position: absolute; border-radius: 50%; pointer-events: none; }
    @keyframes pulse-slow { 0% { transform:scale(0.5);opacity:0.8; } 100% { transform:scale(4);opacity:0; } }
    @keyframes pulse-fast { 0% { transform:scale(0.5);opacity:0.9; } 100% { transform:scale(3);opacity:0; } }
    @keyframes pulse-beat { 0%,100% { transform:scale(1);opacity:0.9; } 50% { transform:scale(1.3);opacity:0.5; } }
    .maplibregl-ctrl-attrib { background:rgba(10,14,23,0.7)!important; color:#555!important; font-size:10px!important; }
    .maplibregl-ctrl-attrib a { color:#555!important; }
  </style>
</head>
<body>
<div id="map"></div>
<script>
  const MIDLON     = PLACEHOLDER_MIDLON;
  const MIDLAT     = PLACEHOLDER_MIDLAT;
  const START_LON  = PLACEHOLDER_START_LON;
  const START_LAT  = PLACEHOLDER_START_LAT;
  const END_LON    = PLACEHOLDER_END_LON;
  const END_LAT    = PLACEHOLDER_END_LAT;
  const START_NAME = PLACEHOLDER_START_NAME;
  const END_NAME   = PLACEHOLDER_END_NAME;
  const routeData  = PLACEHOLDER_ROUTE;
  const poisData   = PLACEHOLDER_POIS;
  const poiColors  = PLACEHOLDER_POI_COLORS;
  const jobsData   = PLACEHOLDER_JOBS;

  const SECTOR_LUCIDE = {
    'IT': 'monitor', 'Banking': 'landmark', 'Healthcare': 'activity',
    'Security': 'shield', 'Other': 'briefcase',
  };

  function lucideSVG(name, size, color) {
    if (typeof lucide === 'undefined' || !lucide.icons[name]) return '';
    var icon = lucide.icons[name];
    var contents = icon[2].map(function(node) {
      if (!node) return '';
      var tag = node[0]; var attrs = node[1] || {};
      var attrStr = Object.keys(attrs).map(function(k) { return k+'="'+attrs[k]+'"'; }).join(' ');
      return '<'+tag+' '+attrStr+'/>';
    }).join('');
    return '<svg xmlns="http://www.w3.org/2000/svg" width="'+size+'" height="'+size+'"'
      +' viewBox="0 0 24 24" fill="none" stroke="'+color+'" stroke-width="2"'
      +' stroke-linecap="round" stroke-linejoin="round" style="vertical-align:middle;flex-shrink:0;">'
      +contents+'</svg>';
  }

  var SVG_BUILDING = '<svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/></svg>';
  var SVG_MAPPIN   = '<svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>';
  var SVG_ARROW    = '<svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>';

  const map = new maplibregl.Map({
    container: 'map',
    style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
    center: [START_LON, START_LAT],
    zoom: 14,
    pitch: 52,
    bearing: -15,
    antialias: true,
  });

  function applyTerrainTints() {
    map.getStyle().layers.forEach(function(layer) {
      var sl = (layer['source-layer'] || '').toLowerCase();
      var id = layer.id.toLowerCase();
      var type = layer.type;
      var isWater = sl==='water'||sl==='waterway'||id.includes('water')||id.includes('river')||id.includes('lake')||id.includes('dam');
      var isGreen = !isWater&&(sl==='landcover'||sl==='landuse'||id.includes('park')||id.includes('grass')||id.includes('wood')||id.includes('forest')||id.includes('farm')||id.includes('meadow')||id.includes('landcover')||id.includes('landuse'));
      if (isWater) {
        try {
          if (type==='fill'){map.setPaintProperty(layer.id,'fill-color','#0a3d55');map.setPaintProperty(layer.id,'fill-opacity',0.9);}
          else if(type==='line'){map.setPaintProperty(layer.id,'line-color','#1a6e8c');map.setPaintProperty(layer.id,'line-opacity',1);map.setPaintProperty(layer.id,'line-width',1.5);}
        } catch(e) {}
      }
      if (isGreen&&type==='fill') {
        try{map.setPaintProperty(layer.id,'fill-color','#0d2b1a');map.setPaintProperty(layer.id,'fill-opacity',0.82);}catch(e){}
      }
    });
  }

  map.on('load', function() {
    applyTerrainTints();
    map.once('idle', applyTerrainTints);

    var labelLayerId;
    for (var i=0; i<map.getStyle().layers.length; i++) {
      var l = map.getStyle().layers[i];
      if (l.type==='symbol' && l.layout['text-field']) { labelLayerId=l.id; break; }
    }
    var styleSource = 'openmaptiles';
    var sources = map.getStyle().sources;
    for (var sid in sources) { if (sources[sid].type==='vector') { styleSource=sid; break; } }

    // 3D buildings
    map.addLayer({
      id:'3d-buildings', source:styleSource, 'source-layer':'building',
      type:'fill-extrusion', minzoom:13,
      paint:{
        'fill-extrusion-color':'BUILDING_COLOR',
        'fill-extrusion-height':0, 'fill-extrusion-base':0,
        'fill-extrusion-height-transition':{duration:2000,delay:300},
        'fill-extrusion-base-transition':{duration:2000,delay:300},
        'fill-extrusion-opacity':0.85,
      }
    }, labelLayerId);
    setTimeout(function() {
      map.setPaintProperty('3d-buildings','fill-extrusion-height',['interpolate',['linear'],['zoom'],13,0,14.05,['coalesce',['get','render_height'],['get','height'],0]]);
      map.setPaintProperty('3d-buildings','fill-extrusion-base',  ['interpolate',['linear'],['zoom'],13,0,14.05,['coalesce',['get','render_min_height'],['get','min_height'],0]]);
    }, 100);

    // Route
    map.addSource('route', { type:'geojson', data:routeData });
    map.addLayer({ id:'route-glow', type:'line', source:'route',
      layout:{'line-join':'round','line-cap':'round'},
      paint:{'line-color':'ROUTE_COLOR','line-width':18,'line-opacity':0.15,'line-blur':8}
    });
    map.addLayer({ id:'route-line', type:'line', source:'route',
      layout:{'line-join':'round','line-cap':'round'},
      paint:{'line-color':'ROUTE_COLOR','line-width':3.5,'line-opacity':0.9}
    });

    // POI pulses
    function createDataPulse(lng, lat, intensity, color) {
      var anim = intensity>0.8 ? 'pulse-fast 0.8s infinite' : intensity>0.5 ? 'pulse-slow 1.2s infinite' : 'pulse-beat 1.5s infinite';
      var el = document.createElement('div');
      var size = 12 + intensity*8;
      el.className = 'data-pulse';
      el.style.cssText = 'width:'+size+'px;height:'+size+'px;background:'+color+';box-shadow:0 0 '+(15+intensity*15)+'px '+color+';animation:'+anim+';border:2px solid rgba(255,255,255,0.3);';
      new maplibregl.Marker({element:el,anchor:'center'}).setLngLat([lng,lat]).addTo(map);
      var label = poisData.find(function(p){return Math.abs(p.lon-lng)<0.0001&&Math.abs(p.lat-lat)<0.0001;});
      if (label) {
        setTimeout(function(){
          var pop = new maplibregl.Popup({closeButton:false,closeOnClick:false,offset:25})
            .setLngLat([lng,lat])
            .setHTML('<div class="marker-label" style="border-left:3px solid '+color+';">'+label.name+'</div>')
            .addTo(map);
          setTimeout(function(){pop.remove();},3000);
        }, intensity*500);
      }
    }

    function createRipple(lng, lat, color, maxRadius) {
      maxRadius = maxRadius||50; var step=0;
      var el = document.createElement('div');
      el.style.cssText='position:absolute;border-radius:50%;border:2px solid '+color+';background:transparent;pointer-events:none;';
      var m = new maplibregl.Marker({element:el,anchor:'center'}).setLngLat([lng,lat]).addTo(map);
      function go(){
        step+=2; if(step>maxRadius){m.remove();return;}
        var s=step*2;
        el.style.width=s+'px';el.style.height=s+'px';
        el.style.opacity=1-(step/maxRadius);
        el.style.marginLeft=-(s/2)+'px';el.style.marginTop=-(s/2)+'px';
        requestAnimationFrame(go);
      }
      go();
    }

    poisData.forEach(function(poi,i){
      var color=poiColors[poi.type]||poiColors.default;
      createDataPulse(poi.lon,poi.lat,poi.intensity,color);
      if(poi.intensity>0.7)  setTimeout(function(){createRipple(poi.lon,poi.lat,color,60);},i*300);
      if(poi.intensity>0.85) setTimeout(function(){createRipple(poi.lon,poi.lat,color,80);},i*300+1500);
    });

    // Heatmap
    map.addSource('poi-heatmap',{type:'geojson',data:{type:'FeatureCollection',
      features:poisData.map(function(p){return{type:'Feature',geometry:{type:'Point',coordinates:[p.lon,p.lat]},properties:{intensity:p.intensity}};})
    }});
    map.addLayer({id:'poi-heatmap-layer',type:'heatmap',source:'poi-heatmap',maxzoom:15,
      paint:{
        'heatmap-weight':['get','intensity'],'heatmap-intensity':0.8,
        'heatmap-color':['interpolate',['linear'],['heatmap-density'],
          0,'rgba(0,0,0,0)',0.2,'rgba(0,255,255,0.2)',0.4,'rgba(0,255,255,0.4)',
          0.6,'rgba(0,150,255,0.6)',0.8,'rgba(255,0,150,0.8)',1,'rgba(255,0,255,1)'
        ],
        'heatmap-radius':40,'heatmap-opacity':0.4,
      }
    },labelLayerId);

    // Start / End markers
    function addEndMarker(lon,lat,label,color,isStart){
      var el=document.createElement('div');
      el.style.cssText='width:20px;height:20px;border-radius:50%;background:'+color+';box-shadow:0 0 30px '+color+';animation:pulse-fast 1s infinite;border:3px solid white;';
      new maplibregl.Marker({element:el,anchor:'center'}).setLngLat([lon,lat]).addTo(map);
      new maplibregl.Popup({closeButton:false,closeOnClick:false,offset:30})
        .setLngLat([lon,lat])
        .setHTML('<div class="marker-label" style="border-left:3px solid '+color+';font-weight:bold;">'+label+'</div>')
        .addTo(map);
      if(isStart) setInterval(function(){createRipple(lon,lat,color,40);},3000);
    }
    addEndMarker(START_LON,START_LAT,START_NAME,'ROUTE_COLOR',true);
    addEndMarker(END_LON,  END_LAT,  END_NAME,  '#ff6b35',    false);

    // Live job pins (GPU canvas layers)
    if (jobsData.length > 0) {
      var features = jobsData.map(function(job){
        return {
          type:'Feature',
          geometry:{type:'Point',coordinates:[job.lon,job.lat]},
          properties:{title:job.title,company:job.company,location:job.location,sector:job.sector,color:job.color,url:job.url}
        };
      });
      map.addSource('jobs',{type:'geojson',data:{type:'FeatureCollection',features:features}});
      map.addLayer({id:'job-glow',type:'circle',source:'jobs',
        paint:{'circle-radius':18,'circle-color':['get','color'],'circle-opacity':0.2,'circle-blur':1}
      });
      map.addLayer({id:'job-dot',type:'circle',source:'jobs',
        paint:{'circle-radius':7,'circle-color':['get','color'],'circle-stroke-width':2,'circle-stroke-color':'rgba(255,255,255,0.4)','circle-opacity':1}
      });
      var activePopup=null;
      map.on('click','job-dot',function(e){
        var p=e.features[0].properties;
        var coords=e.features[0].geometry.coordinates.slice();
        var color=p.color; var bg22=color+'22'; var bg44=color+'44';
        var iconName=SECTOR_LUCIDE[p.sector]||'briefcase';
        var sectorIcon=lucideSVG(iconName,12,color);
        if(activePopup){activePopup.remove();activePopup=null;}
        activePopup=new maplibregl.Popup({closeButton:true,closeOnClick:true,offset:14,maxWidth:'300px'})
          .setLngLat(coords)
          .setHTML(
            '<div class="job-popup-inner" style="border-top:2px solid '+color+';border-radius:10px;">'
            +'<div class="job-popup-sector" style="color:'+color+';">'+sectorIcon+p.sector+'</div>'
            +'<div class="job-popup-title">'+p.title+'</div>'
            +'<div class="job-popup-meta">'+SVG_BUILDING+p.company+'</div>'
            +'<div class="job-popup-meta">'+SVG_MAPPIN+p.location+'</div>'
            +'<a href="'+p.url+'" target="_blank" rel="noopener" class="job-popup-apply"'
            +' style="background:'+bg22+';border:1px solid '+bg44+';color:'+color+';">'
            +'View &amp; Apply '+SVG_ARROW+'</a>'
            +'</div>'
          ).addTo(map);
      });
      map.on('mouseenter','job-dot',function(){map.getCanvas().style.cursor='pointer';});
      map.on('mouseleave','job-dot',function(){map.getCanvas().style.cursor='';});
    }

    // ── Two-stage cinematic fly-in ─────────────────────────────────────────────
    // Stage 1: zoom into the user's start address at street level
    setTimeout(function() {
      map.flyTo({
        center: [START_LON, START_LAT],
        zoom: 15.5, pitch: 60, bearing: 0,
        duration: 2000, essential: true,
      });
    }, 400);

    // Stage 2: pull back to frame the entire route perfectly
    setTimeout(function() {
      var coords = routeData.geometry.coordinates;
      var lngs = coords.map(function(c){return c[0];});
      var lats = coords.map(function(c){return c[1];});
      var bounds = [
        [Math.min.apply(null,lngs), Math.min.apply(null,lats)],
        [Math.max.apply(null,lngs), Math.max.apply(null,lats)],
      ];
      map.fitBounds(bounds, {
        padding: {top:80, bottom:80, left:80, right:80},
        pitch: 52, bearing: -15,
        duration: 2800, essential: true,
      });
    }, 2800);
  });
</script>
</body>
</html>"""

    html = html.replace("BG_COLOR",              _BG)
    html = html.replace("ROUTE_COLOR",            _ROUTE_COLOR)
    html = html.replace("BUILDING_COLOR",         _BUILDING_COLOR)
    html = html.replace("PLACEHOLDER_MIDLON",     str(midpoint_lon))
    html = html.replace("PLACEHOLDER_MIDLAT",     str(midpoint_lat))
    html = html.replace("PLACEHOLDER_START_LON",  str(start_lon))
    html = html.replace("PLACEHOLDER_START_LAT",  str(start_lat))
    html = html.replace("PLACEHOLDER_END_LON",    str(end_lon))
    html = html.replace("PLACEHOLDER_END_LAT",    str(end_lat))
    html = html.replace("PLACEHOLDER_START_NAME", start_name_js)
    html = html.replace("PLACEHOLDER_END_NAME",   end_name_js)
    html = html.replace("PLACEHOLDER_ROUTE",      route_json_str_escaped)
    html = html.replace("PLACEHOLDER_POIS",       pois_json)
    html = html.replace("PLACEHOLDER_POI_COLORS", poi_colors_js)
    html = html.replace("PLACEHOLDER_JOBS",       jobs_json)

    return html