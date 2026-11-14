import { useEffect, useState } from "react";

const BASE = import.meta.env.VITE_API_BASE ?? "";

export function queryURL(path, params = {}) {
  const query = new URLSearchParams(Object.entries(params).filter(([, value]) => value !== undefined && value !== ""));
  return `${BASE}${path}${query.size ? `?${query}` : ""}`;
}

export async function request(url, options = {}) {
  const response = await fetch(url, options);
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = Array.isArray(body.detail)
      ? body.detail.map((item) => `${item.loc?.slice(1).join(".") || "Input"}: ${item.msg}`).join("; ")
      : body.detail;
    throw new Error(typeof detail === "string" ? detail : `Request failed (${response.status}).`);
  }
  return body;
}

export function useParva(path, params = {}) {
  const url = path ? queryURL(path, params) : null;
  const [state, setState] = useState({ url: null, loading: true });
  useEffect(() => {
    if (!url) return;
    const controller = new AbortController();
    request(url, { signal: controller.signal })
      .then((body) => !controller.signal.aborted && setState({ ...body, url, loading: false }))
      .catch((error) => !controller.signal.aborted && setState({ url, error: error.message, loading: false }));
    return () => controller.abort();
  }, [url]);
  // A changed query must never render a previous date's answer while loading.
  return state.url === url && url ? state : { loading: Boolean(url) };
}

export const todayISO = () => new Date().toLocaleDateString("sv-SE", { timeZone: "Asia/Kathmandu" });
export const fmt = (iso) => iso
  ? new Date(`${iso}T00:00:00`).toLocaleDateString("en-GB", { weekday: "short", day: "numeric", month: "short", year: "numeric" })
  : "Not established";
export const workingLabel = (working) => working === null ? "Not established" : working ? "Working day" : "Non-working day";
