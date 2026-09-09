/**
 * THERMALIS-X MapViewer Component (Leaflet 1.9.4)
 */
export class MapViewer {
  constructor(elementId, initialCenter = [20.5937, 78.9629], initialZoom = 5) {
    this.map = L.map(elementId, {
      zoomControl: false,
      attributionControl: false
    }).setView(initialCenter, initialZoom);

    L.control.zoom({ position: 'bottomright' }).addTo(this.map);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 19,
      subdomains: 'abcd'
    }).addTo(this.map);

    this.eventLayer = L.layerGroup().addTo(this.map);
    this.facilityLayer = L.layerGroup().addTo(this.map);
  }

  clearEvents() {
    this.eventLayer.clearLayers();
  }

  addEventMarker(event, onClickCallback) {
    const color = event.priority === 'CRITICAL' ? '#ef4444' :
                  event.priority === 'HIGH' ? '#f97316' :
                  event.priority === 'WATCH' ? '#3b82f6' : '#10b981';

    const circle = L.circleMarker([event.centroid_lat, event.centroid_lon], {
      radius: Math.max(6, Math.min(22, Math.sqrt(event.max_frp) * 2.2)),
      fillColor: color,
      color: '#ffffff',
      weight: 1.5,
      opacity: 0.9,
      fillOpacity: 0.75
    });

    circle.bindTooltip(`<b>${event.id}</b><br>${event.source_class} (${event.max_frp} MW)`, {
      permanent: false,
      direction: 'top',
      className: 'leaflet-tooltip-dark'
    });

    circle.on('click', () => onClickCallback(event));
    this.eventLayer.addLayer(circle);
    return circle;
  }

  flyTo(lat, lon, zoom = 13) {
    this.map.flyTo([lat, lon], zoom, { duration: 1.2 });
  }
}
