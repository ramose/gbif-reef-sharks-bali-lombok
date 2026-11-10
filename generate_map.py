#!/usr/bin/env python3
"""Build gbif-reef-sharks-bali-lombok-map.html from the live GBIF fetch.

Data source (fetched live 2026-11-09, Asia/Makassar):
https://api.gbif.org/v1/occurrence/search?taxonKey=2418054&taxonKey=2417981&taxonKey=2418064&decimalLongitude=114,117&decimalLatitude=-9.5,-8&hasCoordinate=true&limit=300
168 records: 129 whitetip (Triaenodon obesus), 31 blacktip reef
(Carcharhinus melanopterus), 8 grey reef (Carcharhinus amblyrhynchos).
"""
import json

compact = json.load(open('/tmp/gbif_sharks_compact.json'))
data_json = json.dumps(compact)

html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GBIF Reef Shark Sightings — Bali &amp; Lombok</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css">
<link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css">
<style>
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #1f2937; background: #f8fafc; }
  header { padding: 14px 16px 10px; }
  h1 { font-size: 18px; margin: 0 0 4px; }
  p.sub { margin: 0 0 10px; font-size: 13px; color: #64748b; line-height: 1.45; }
  .stats { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 10px; }
  .stat { background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 8px 12px; font-size: 13px; }
  .stat b { font-size: 16px; display: block; }
  .dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 5px; vertical-align: -1px; }
  .filters { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; padding: 0 16px 10px; font-size: 13px; }
  .filters label { background: #fff; border: 1px solid #e2e8f0; border-radius: 999px; padding: 5px 10px; cursor: pointer; user-select: none; }
  .filters label.off { opacity: 0.45; }
  .filters select { padding: 5px 8px; border-radius: 999px; border: 1px solid #e2e8f0; background: #fff; font-size: 13px; }
  #count { margin-left: auto; color: #64748b; }
  #map { height: 560px; width: 100%; border-top: 1px solid #e2e8f0; }
  footer { padding: 10px 16px 16px; font-size: 12px; color: #64748b; line-height: 1.5; }
  footer a { color: #0e7490; }
  .pin { width: 14px; height: 14px; border-radius: 50% 50% 50% 0; transform: rotate(-45deg); border: 2px solid #fff; box-shadow: 0 1px 4px rgba(0,0,0,.4); }
  .leaflet-popup-content { font-size: 13px; line-height: 1.5; }
  .leaflet-popup-content b { font-size: 14px; }
  .leaflet-popup-content i { color: #475569; }
</style>
</head>
<body>
<header>
  <h1>Reef shark sightings — Bali &amp; Lombok</h1>
  <p class="sub">Every GBIF occurrence record with coordinates in the Bali–Lombok box
  (lon 114–117, lat −9.5 to −8). These are sighting records, not live tracking —
  reef sharks here are mostly resident on one reef.</p>
  <div class="stats">
    <div class="stat"><b>168</b>records</div>
    <div class="stat"><b><span class="dot" style="background:#0e7490"></span>129</b>Whitetip reef shark</div>
    <div class="stat"><b><span class="dot" style="background:#b45309"></span>31</b>Blacktip reef shark</div>
    <div class="stat"><b><span class="dot" style="background:#475569"></span>8</b>Grey reef shark</div>
    <div class="stat"><b>2002 – 2026</b>26 Mar 2002 → 15 Sep 2026</div>
  </div>
</header>
<div class="filters">
  <label data-sp="Triaenodon obesus"><input type="checkbox" checked> <span class="dot" style="background:#0e7490"></span>Whitetip (129)</label>
  <label data-sp="Carcharhinus melanopterus"><input type="checkbox" checked> <span class="dot" style="background:#b45309"></span>Blacktip (31)</label>
  <label data-sp="Carcharhinus amblyrhynchos"><input type="checkbox" checked> <span class="dot" style="background:#475569"></span>Grey (8)</label>
  <select id="years" title="Filter by year">
    <option value="0">All years</option>
    <option value="2020">2020 and later</option>
    <option value="2024">2024 and later</option>
  </select>
  <span id="count"></span>
</div>
<div id="map"></div>
<footer>
  Source: <a href="https://www.gbif.org/" target="_blank" rel="noopener">GBIF</a> occurrence search,
  fetched live 9 Nov 2026 — mainly iNaturalist research-grade observations (116) and Diveboard scuba
  citizen science (34). Query: taxonKey 2418054 (whitetip) + 2417981 (blacktip reef) + 2418064 (grey reef),
  decimalLongitude 114,117, decimalLatitude −9.5,−8, hasCoordinate=true, limit=300.
  Click any pin for date, locality and the GBIF record. Basemap: OpenFreeMap (OpenStreetMap data);
  switch basemap with the layers control, top right.
</footer>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js"></script>
<script>
const DATA = __DATA__;
const COLORS = {
  "Triaenodon obesus": "#0e7490",
  "Carcharhinus melanopterus": "#b45309",
  "Carcharhinus amblyrhynchos": "#475569"
};

const map = L.map("map").setView([-8.55, 115.45], 9);
const openFreeMap = L.tileLayer("https://tiles.openfreemap.org/planet/{z}/{x}/{y}.png", {
  maxZoom: 19, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://openfreemap.org">OpenFreeMap</a>'
}).addTo(map);
const carto = L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
  maxZoom: 19, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>'
});
const esri = L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
  maxZoom: 19, attribution: "Tiles &copy; Esri &mdash; Source: Esri, Maxar, Earthstar Geographics"
});
L.control.layers({ "OpenFreeMap": openFreeMap, "Carto Light": carto, "Esri Satellite": esri }).addTo(map);

let cluster = null;
function activeSpecies() {
  const on = {};
  document.querySelectorAll(".filters label").forEach(function (lab) {
    on[lab.dataset.sp] = lab.querySelector("input").checked;
  });
  return on;
}
function render() {
  if (cluster) map.removeLayer(cluster);
  const on = activeSpecies();
  const minYear = parseInt(document.getElementById("years").value, 10) || 0;
  const group = (typeof L.markerClusterGroup === "function")
    ? L.markerClusterGroup({ showCoverageOnHover: false, maxClusterRadius: 45 })
    : L.layerGroup();
  let shown = 0;
  DATA.forEach(function (r) {
    if (!on[r.sp]) return;
    const y = r.date ? parseInt(r.date.slice(0, 4), 10) : 0;
    if (minYear && y < minYear) return;
    const icon = L.divIcon({
      className: "", iconSize: [14, 14], iconAnchor: [7, 13],
      html: '<div class="pin" style="background:' + (COLORS[r.sp] || "#334155") + '"></div>'
    });
    const m = L.marker([r.lat, r.lon], { icon: icon });
    const loc = r.loc ? r.loc : "Locality not recorded";
    const date = r.date ? r.date : "Date not recorded";
    m.bindPopup("<b>" + r.cn + "</b><br><i>" + r.sp + "</i><br>Date: " + date +
      "<br>Place: " + loc + "<br>Source: " + (r.src || "GBIF") +
      '<br><a href="https://www.gbif.org/occurrence/' + r.k + '" target="_blank" rel="noopener">GBIF record ' + r.k + " &rarr;</a>");
    group.addLayer(m);
    shown++;
  });
  cluster = group;
  map.addLayer(cluster);
  document.getElementById("count").textContent = shown + " of 168 shown";
  if (shown) {
    const pts = DATA.filter(function (r) { return on[r.sp] && (!minYear || (r.date && parseInt(r.date.slice(0,4),10) >= minYear)); })
      .map(function (r) { return [r.lat, r.lon]; });
    if (pts.length) map.fitBounds(pts, { padding: [30, 30] });
  }
}
document.querySelectorAll(".filters label input").forEach(function (cb) {
  cb.addEventListener("change", function () {
    cb.closest("label").classList.toggle("off", !cb.checked);
    render();
  });
});
document.getElementById("years").addEventListener("change", render);
render();
</script>
</body>
</html>
"""

html = html.replace("__DATA__", data_json)
import os
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gbif-reef-sharks-bali-lombok-map.html")
open(out, "w").write(html)
print("wrote", out, len(html), "bytes,", len(compact), "records")
