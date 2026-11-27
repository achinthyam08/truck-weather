import { useCallback, useState } from "react";
import { fetchPlan } from "./api";
import ForecastSlider from "./components/ForecastSlider";
import RouteList from "./components/RouteList";
import TripForm from "./components/TripForm";
import TripMap from "./components/TripMap";
import "./App.css";

export default function App() {
  const [plan, setPlan] = useState(null);
  const [selectedId, setSelectedId] = useState(0);
  const [hour, setHour] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const select = useCallback((id) => setSelectedId(id), []);

  async function handleSubmit(trip) {
    setLoading(true);
    setError("");
    setPlan(null);
    try {
      const result = await fetchPlan(trip);
      setSelectedId(result.recommended_id);
      setHour(0);
      setPlan(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="layout">
      <aside className="sidebar">
        <h1>Truck Weather Routing</h1>
        <TripForm loading={loading} onSubmit={handleSubmit} />
        {loading && <p role="status">Finding routes and checking the weather…</p>}
        {error && <p className="warning" role="alert">{error}</p>}
        {plan && <RouteList plan={plan} selectedId={selectedId} onSelect={select} />}
      </aside>
      <main className="map-area">
        <TripMap plan={plan} selectedId={selectedId} onSelect={select} hour={hour} />
        {plan && <ForecastSlider start={plan.heatmap_start} hour={hour} onChange={setHour} />}
      </main>
    </div>
  );
}
