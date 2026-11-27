import { RISK, formatTime } from "../format";

export default function ForecastSlider({ start, hour, onChange }) {
  const time = new Date(new Date(start).getTime() + hour * 3600000);
  return (
    <div className="slider">
      <label>
        Corridor forecast: <strong>+{hour} h</strong> · {formatTime(time)}
        <input type="range" min="0" max="48" value={hour} onChange={(e) => onChange(Number(e.target.value))} />
      </label>
      <ul className="legend">
        {RISK.map((r) => (
          <li key={r.label}><i style={{ background: r.color }} />{r.label}</li>
        ))}
      </ul>
    </div>
  );
}
