export const RISK = [
  { label: "Low", color: "#16a34a" },
  { label: "Moderate", color: "#eab308" },
  { label: "High", color: "#f97316" },
  { label: "Severe", color: "#dc2626" },
  { label: "No Travel", color: "#7e22ce" },
];

export const ROUTE_COLORS = ["#2563eb", "#0f172a", "#0891b2"];

export const formatTime = (value) =>
  new Date(value).toLocaleString([], {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

export function formatHours(hours) {
  const minutes = Math.round(hours * 60);
  return `${Math.floor(minutes / 60)}h ${minutes % 60}m`;
}

/** Value for <input type="datetime-local">, in the browser's time zone. */
export function toLocalInput(date) {
  const shifted = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
  return shifted.toISOString().slice(0, 16);
}
