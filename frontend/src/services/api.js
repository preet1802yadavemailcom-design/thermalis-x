/**
 * THERMALIS-X REST API Service Client
 */
const API_BASE = '/api/v1';

export async function fetchEvents() {
  const res = await fetch(`${API_BASE}/events`);
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
}

export async function fetchEventDetail(eventId) {
  const res = await fetch(`${API_BASE}/events/${eventId}`);
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
}

export async function fetchFacilities() {
  const res = await fetch(`${API_BASE}/facilities`);
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
}

export async function fetchAlerts() {
  const res = await fetch(`${API_BASE}/alerts`);
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
}

export async function fetchReplayCases() {
  const res = await fetch(`${API_BASE}/replay/cases`);
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
}

export async function fetchReplaySteps(caseId) {
  const res = await fetch(`${API_BASE}/replay/cases/${caseId}/steps`);
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
}

export async function fetchResponsePlan(eventId) {
  const res = await fetch(`${API_BASE}/events/${eventId}/response-plan`);
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
}

export async function fetchIcs201Brief(eventId) {
  const res = await fetch(`${API_BASE}/events/${eventId}/ics-201`);
  if (!res.ok) throw new Error(`HTTP error ${res.status}`);
  return await res.json();
}
