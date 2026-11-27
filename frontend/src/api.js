/**
 * api.js — thin wrapper around the backend base URL.
 *
 * VITE_API_BASE_URL is injected at build time by Vite from the .env file.
 * Default to http://127.0.0.1:8000 for local development.
 */
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

/**
 * Fetch the health endpoint.
 * @returns {Promise<{status: string, version: string, service: string}>}
 */
export async function fetchHealth() {
  const response = await fetch(`${BASE_URL}/api/health`);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status} from ${BASE_URL}/api/health`);
  }
  return response.json();
}
