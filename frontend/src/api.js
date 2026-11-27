const BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

export async function fetchPlan(trip) {
  let response;
  try {
    response = await fetch(`${BASE_URL}/api/plan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(trip),
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
