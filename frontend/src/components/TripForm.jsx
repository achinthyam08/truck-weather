import { useState } from "react";
import { toLocalInput } from "../format";

export default function TripForm({ loading, onSubmit }) {
  const [trip, setTrip] = useState(() => ({
    origin: "Chicago, IL",
    destination: "Denver, CO",
    departure: toLocalInput(new Date(Date.now() + 60 * 60 * 1000)),
    load_lb: "42000",
    interval_miles: "25",
  }));

  const field = (name) => ({
    name,
    value: trip[name],
    required: true,
    onChange: (e) => setTrip({ ...trip, [name]: e.target.value }),
  });

  function submit(event) {
    event.preventDefault();
    onSubmit({
      ...trip,
      departure: new Date(trip.departure).toISOString(),
      load_lb: Number(trip.load_lb),
      interval_miles: Number(trip.interval_miles),
    });
  }

  return (
    <form className="form" onSubmit={submit}>
      <label>Origin<input {...field("origin")} /></label>
      <label>Destination<input {...field("destination")} /></label>
      <label>Departure (your local time)<input type="datetime-local" {...field("departure")} /></label>
      <label>Load weight (lb)<input type="number" min="0" max="80000" {...field("load_lb")} /></label>
      <label>
        Weather checkpoint spacing
        <select {...field("interval_miles")}>
          <option value="10">Every 10 miles</option>
          <option value="25">Every 25 miles</option>
          <option value="50">Every 50 miles</option>
        </select>
      </label>
      <button disabled={loading}>{loading ? "Planning…" : "Plan route"}</button>
    </form>
  );
}
