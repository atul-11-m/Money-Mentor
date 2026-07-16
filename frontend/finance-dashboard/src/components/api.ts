const BASE_URL = "http://localhost:5001";

export async function fetchSummary(start?: string, end?: string) {
  let url = `${BASE_URL}/summary`;
  if (start && end) url += `?start_date=${start}&end_date=${end}`;
  const res = await fetch(url);
  return res.json();
}

export async function fetchTimeline(start?: string, end?: string) {
  let url = `${BASE_URL}/timeline`;
  if (start && end) url += `?start_date=${start}&end_date=${end}`;
  const res = await fetch(url);
  return res.json();
}

export async function fetchTotal(start?: string, end?: string) {
  let url = `${BASE_URL}/total`;
  if (start && end) url += `?start_date=${start}&end_date=${end}`;
  const res = await fetch(url);
  return res.json();
}

export async function fetchIncome(start?: string, end?: string) {
  let url = `${BASE_URL}/income`;
  if (start && end) url += `?start_date=${start}&end_date=${end}`;
  const res = await fetch(url);
  return res.json();
}

export async function fetchBalance(start?: string, end?: string) {
  let url = `${BASE_URL}/balance`;
  if (start && end) url += `?start_date=${start}&end_date=${end}`;
  const res = await fetch(url);
  return res.json();
}

export async function fetchTimelineByCategory(category: string, start?: string, end?: string) {
  let url = `${BASE_URL}/timeline/${encodeURIComponent(category)}`;
  if (start && end) url += `?start_date=${start}&end_date=${end}`;
  const res = await fetch(url);
  return res.json();
}

export async function fetchCategoryBar(start?: string, end?: string) {
  let url = `${BASE_URL}/categories/bar`;
  if (start && end) url += `?start_date=${start}&end_date=${end}`;
  const res = await fetch(url);
  return res.json();
}

export async function uploadCSV(file: File) {
  const url = `${BASE_URL}/upload`;
  const fd = new FormData();
  fd.append("file", file);

  const res = await fetch(url, {
    method: "POST",
    body: fd,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Upload failed with status ${res.status}`);
  }

  return res.json();
}
