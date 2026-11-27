const URL = "https://api.open-meteo.com/v1/forecast";
const BATCH = 100;
const TTL_MS = 30 * 60 * 1000;
const cache = new Map();

async function download(cells, params) {
  const query = new URLSearchParams({
    ...params,
    latitude: cells.map((c) => c.lat).join(","),
    longitude: cells.map((c) => c.lon).join(","),
  });
  const response = await fetch(`${URL}?${query}`).catch(() => null);
  const data = await response?.json().catch(() => null);
  if (!response?.ok || !data) {
    throw new Error(`Weather service error: ${data?.reason ?? "please try again"}`);
  }
  return Array.isArray(data) ? data : [data];
}

/** Returns {cellKey: hourly forecast}, cached for 30 minutes. */
export async function fetchWeather({ cells, params }) {
  const window = `${params.start_hour}|${params.end_hour}`;
  const result = {};
  const missing = cells.filter((cell) => {
    const hit = cache.get(`${cell.key}|${window}`);
    if (!hit || Date.now() - hit.saved > TTL_MS) return true;
    result[cell.key] = hit.hourly;
    return false;
  });

  for (let i = 0; i < missing.length; i += BATCH) {
    const batch = missing.slice(i, i + BATCH);
    const items = await download(batch, params);
    batch.forEach((cell, n) => {
      result[cell.key] = items[n].hourly;
      cache.set(`${cell.key}|${window}`, { saved: Date.now(), hourly: items[n].hourly });
    });
  }
  return result;
}
