import { RISK, ROUTE_COLORS, formatHours, formatTime } from "../format";

export default function RouteList({ plan, selectedId, onSelect }) {
  const selected = plan.routes[selectedId];
  return (
    <section>
      {plan.warnings.map((w) => (
        <p key={w} className="warning" role="alert">{w}</p>
      ))}
      <p className="reason">
        <strong>{plan.routes[plan.recommended_id].name} is recommended.</strong> {plan.reason}
      </p>

      {plan.routes.map((route) => {
        const s = route.summary;
        return (
          <button
            key={route.id}
            className={`route-card ${route.id === selectedId ? "active" : ""}`}
            onClick={() => onSelect(route.id)}
          >
            <span className="route-title">
              <i style={{ background: ROUTE_COLORS[route.id] }} />
              {route.name}
              {route.id === plan.recommended_id && <em>Recommended</em>}
            </span>
            <span>{route.miles} mi · {formatHours(s.duration_hours)} · arrives {formatTime(route.arrival)}</span>
            <span>No Travel {s.no_travel_miles} mi · Severe {s.severe_miles} mi · High {s.high_miles} mi</span>
            <span>
              Average risk {s.average_risk} · Worst{" "}
              <b style={{ color: RISK[s.max_level].color }}>{RISK[s.max_level].label}</b>
            </span>
          </button>
        );
      })}

      <h2>{selected.name} checkpoints</h2>
      <div className="table-wrap">
        <table>
          <thead>
            <tr><th>Mile</th><th>ETA</th><th>Wind</th><th>Rain</th><th>Snow</th><th>Risk</th></tr>
          </thead>
          <tbody>
            {selected.checkpoints.map((c) => (
              <tr key={c.mile}>
                <td>{c.mile}</td>
                <td>{formatTime(c.eta)}</td>
                <td>{Math.round(c.wind)}</td>
                <td>{c.rain.toFixed(2)}</td>
                <td>{c.snow.toFixed(2)}</td>
                <td style={{ color: RISK[c.level].color }}>{RISK[c.level].label}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="note">Wind in mph. Rain and snow in inches per hour.</p>
    </section>
  );
}
