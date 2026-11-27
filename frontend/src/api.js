import { fetchWeather } from "./weather";

const BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

async function postPlan(body) {
  let response;
  try {
    response = await fetch(`${BASE_URL}/api/plan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    throw new Error("Could not reach the server. Check that the backend is running.");
  }
  const data = await response.json().catch(() => null);
  if (!response.ok || !data) {
    throw new Error(data?.error ?? `Server error (${response.status}).`);
  }
  return data;
}

/** The server asks for forecasts; the browser downloads them and asks again. */
export async function fetchPlan(trip) {
  const weather = {};
  for (let attempt = 0; attempt < 3; attempt += 1) {
    const data = await postPlan({ ...trip, weather });
    if (!data.weather_request) return data;
    Object.assign(weather, await fetchWeather(data.weather_request));
  }
  throw new Error("Could not collect all the weather data. Please try again.");
}
