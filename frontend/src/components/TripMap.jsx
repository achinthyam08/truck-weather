import { Fragment, memo, useEffect } from "react";
import { Circle, CircleMarker, MapContainer, Polyline, Popup, TileLayer, Tooltip, useMap } from "react-leaflet";
import { RISK, ROUTE_COLORS, formatTime } from "../format";

function FitBounds({ plan }) {
  const map = useMap();
  useEffect(() => {
    if (plan) map.fitBounds(plan.routes.flatMap((r) => r.geometry), { padding: [30, 30] });
  }, [map, plan]);
  return null;
}

// Memoised so moving the slider only redraws the heatmap.
const Routes = memo(function Routes({ plan, selectedId, onSelect }) {
  // Draw the selected route last so it sits on top.
  const ordered = [...plan.routes].sort((a, b) => (a.id === selectedId) - (b.id === selectedId));
  return ordered.map((route) => {
    const active = route.id === selectedId;
    return (
      // The key includes `active` so Leaflet re-adds layers in the new order.
      <Fragment key={`${route.id}-${active}`}>
        <Polyline
          positions={route.geometry}
          pathOptions={{ color: ROUTE_COLORS[route.id], weight: active ? 6 : 3, opacity: active ? 0.9 : 0.5 }}
          eventHandlers={{ click: () => onSelect(route.id) }}
        >
          <Tooltip sticky>{route.name}</Tooltip>
        </Polyline>
        {route.checkpoints.map((c) => (
          <CircleMarker
            key={c.mile}
            center={[c.lat, c.lon]}
            radius={active ? 6 : 3}
            pathOptions={{ color: "#fff", weight: 1, fillColor: RISK[c.level].color, fillOpacity: 1 }}
          >
            <Popup>
              <strong>{route.name}, mile {c.mile}</strong><br />
              ETA {formatTime(c.eta)}<br />
              Risk: {RISK[c.level].label}<br />
              Wind {Math.round(c.wind)} mph (gusts {Math.round(c.gust)})<br />
              Rain {c.rain.toFixed(2)} in/hr · Snow {c.snow.toFixed(2)} in/hr
            </Popup>
          </CircleMarker>
        ))}
      </Fragment>
    );
  });
});

export default function TripMap({ plan, selectedId, onSelect, hour }) {
  return (
    <MapContainer center={[39.5, -98.35]} zoom={4} preferCanvas className="map">
      <TileLayer
        url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; OpenStreetMap contributors | <a href="https://open-meteo.com/">Weather data by Open-Meteo.com</a>'
      />
      <FitBounds plan={plan} />
      {plan?.heatmap.map((p) => (
        <Circle
          key={`${p.lat},${p.lon}`}
          center={[p.lat, p.lon]}
          radius={30000}
          interactive={false}
          pathOptions={{ stroke: false, fillColor: RISK[p.levels[hour]].color, fillOpacity: 0.25 }}
        />
      ))}
      {plan && <Routes plan={plan} selectedId={selectedId} onSelect={onSelect} />}
    </MapContainer>
  );
}
