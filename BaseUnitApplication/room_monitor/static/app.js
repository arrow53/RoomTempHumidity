"use strict";
const $ = (id) => document.getElementById(id);
let unit = "C", selected = null, hours = 24, state = null, history = null, historyRequest = 0;
let failed = false, lastSuccess = 0, cardSignature = "";
try { unit = localStorage.getItem("roomlight.unit") === "F" ? "F" : "C"; } catch (_) {}
const number = (value) => Number(value).toFixed(1);
const temperature = (c) => unit === "F" ? c * 9 / 5 + 32 : c;
const ageText = (age) => age < 60 ? "Just received" : age < 3600 ? `${Math.floor(age / 60)} min ago` : `${Math.floor(age / 3600)} h ago`;
const statusText = { fresh: "Fresh", stale: "Delayed", offline: "Offline", waiting: "Waiting", clock_error: "Check clock" };
const el = (tag, className, text) => { const node = document.createElement(tag); if (className) node.className = className; if (text !== undefined) node.textContent = text; return node; };

function renderRooms() {
  if (!state) return;
  const active = document.activeElement?.dataset?.node;
  const signature = JSON.stringify([state.rooms, selected, unit, failed]);
  if (signature === cardSignature) return;
  cardSignature = signature;
  const rooms = $("rooms");
  rooms.replaceChildren();
  if (!state.rooms.length) {
    const empty = el("div", "empty-state");
    empty.append(el("strong", "", "Ready for your first room."), el("span", "", "Add your sensor’s hardware ID and room name to config/rooms.json, then restart the collector. Live mode never creates sample readings."));
    rooms.append(empty);
    return;
  }
  state.rooms.forEach(room => {
    const status = failed ? "offline" : room.status;
    const card = el("button", `room-card ${status}`);
    card.dataset.node = room.node_id;
    card.setAttribute("aria-pressed", String(selected === room.node_id));
    card.setAttribute("aria-label", `${room.label}: ${failed ? "collector unreachable" : statusText[status]}. Show history`);
    const top = el("div", "room-top");
    top.append(el("span", "room-label", room.label), el("span", `status ${status}`, failed ? "No connection" : statusText[status]));
    const reading = el("div", "reading");
    reading.append(el("span", "temperature", room.temperature_c === null ? "—" : number(temperature(room.temperature_c))), el("span", "unit", `°${unit}`));
    const humidity = el("div", "humidity");
    humidity.append(el("strong", "", room.humidity_pct === null ? "—" : `${number(room.humidity_pct)}%`), document.createTextNode(" humidity"));
    const bottom = el("div", "room-bottom");
    bottom.append(el("span", "", room.status === "clock_error" ? "Collector time error" : room.age_s === null ? "No reading received" : ageText(room.age_s)), el("span", "", "↗"));
    card.append(top, reading, humidity, bottom);
    card.addEventListener("click", () => { selected = room.node_id; history = null; renderRooms(); renderChart(); fetchHistory(); });
    rooms.append(card);
  });
  if (active) Array.from(rooms.children).find(card => card.dataset.node === active)?.focus({ preventScroll: true });
}

function svg(tag, attrs, text) {
  const node = document.createElementNS("http://www.w3.org/2000/svg", tag);
  Object.entries(attrs || {}).forEach(([key, value]) => node.setAttribute(key, value));
  if (text !== undefined) node.textContent = text;
  return node;
}

function renderChart() {
  const room = state?.rooms.find(room => room.node_id === selected);
  $("history-title").textContent = room ? `${room.label} · history` : "Room history";
  $("history-subtitle").textContent = room ? `Past ${hours === 1 ? "hour" : `${hours} hours`} · temperature and relative humidity` : "Select a room above to explore its readings.";
  $("history-temp").textContent = room?.temperature_c != null ? `${number(temperature(room.temperature_c))}°${unit}` : "—";
  $("history-humidity").textContent = room?.humidity_pct != null ? `${number(room.humidity_pct)}%` : "—";
  const chart = $("chart"); chart.replaceChildren();
  const width = Math.max(240, chart.clientWidth), height = chart.clientHeight;
  chart.setAttribute("viewBox", `0 0 ${width} ${height}`);
  const points = history?.points || [];
  $("chart-empty").hidden = points.length > 0;
  $("chart-empty").textContent = failed ? "Collector unreachable. Reconnecting…" : history === null && room ? "Loading history…" : "No readings in this time range.";
  chart.setAttribute("aria-label", room ? `${room.label}, ${points.length} history buckets over ${hours} hours. Temperature on left axis, humidity on right.` : "No history available");
  if (!points.length) return;
  const values = points.map(p => temperature(p.temperature_c));
  const low = Math.floor(Math.min(...values) - 1), high = Math.ceil(Math.max(...values) + 1);
  const left = 46, right = width - 46, top = 20, bottom = height - 30;
  const x = (time) => left + (time - history.from) / (history.to - history.from) * (right - left);
  const y = (value) => bottom - (value - low) / (high - low) * (bottom - top);
  const hy = (value) => bottom - value / 100 * (bottom - top);
  for (let i = 0; i <= 4; i++) {
    const py = top + (bottom - top) * i / 4;
    chart.append(svg("line", {x1:left,x2:right,y1:py,y2:py,class:"grid"}));
    chart.append(svg("text", {x:left-9,y:py+4,"text-anchor":"end"}, `${number(high-(high-low)*i/4)}°`));
    chart.append(svg("text", {x:right+9,y:py+4}, `${100-i*25}%`));
  }
  const makePath = (getter) => points.map((p, i) => {
    const gap = i === 0 || p.received_at - points[i - 1].received_at > Math.max(state.offline_s, history.bucket_seconds * 2);
    return `${gap ? "M" : "L"}${x(p.received_at).toFixed(1)},${getter(p).toFixed(1)}`;
  }).join(" ");
  chart.append(svg("path", {d:makePath(p=>y(temperature(p.temperature_c))),class:"temp-line"}));
  chart.append(svg("path", {d:makePath(p=>hy(p.humidity_pct)),class:"humidity-line"}));
  if (points.length === 1) {
    chart.append(svg("circle", {cx:x(points[0].received_at),cy:y(temperature(points[0].temperature_c)),r:4,fill:"#4f7851"}));
    chart.append(svg("circle", {cx:x(points[0].received_at),cy:hy(points[0].humidity_pct),r:4,fill:"#ae8250"}));
  }
  const timeTicks = width < 520 ? 2 : 4;
  for (let i = 0; i <= timeTicks; i++) {
    const time = history.from + (history.to - history.from) * i / timeTicks;
    const label = new Date(time*1000).toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"});
    chart.append(svg("text", {x:left+(right-left)*i/timeTicks,y:height-6,"text-anchor":"middle"}, label));
  }
}

async function getJSON(url) {
  const response = await fetch(url, {cache:"no-store",signal:AbortSignal.timeout(5000)});
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

async function fetchHistory() {
  const request = ++historyRequest;
  if (!selected || !state) return;
  const node = selected, range = hours;
  try {
    const result = await getJSON(`/api/history?node_id=${encodeURIComponent(node)}&hours=${range}&limit=240`);
    if (request !== historyRequest || selected !== node || hours !== range) return;
    history = result; renderChart();
  } catch (_) {
    if (request === historyRequest) { history = null; renderChart(); $("chart-empty").hidden = false; $("chart-empty").textContent = "History unavailable. Retrying automatically…"; }
  }
}

async function refresh() {
  try {
    state = await getJSON("/api/status");
    failed = false; lastSuccess = Date.now();
    if (!selected || !state.rooms.some(room => room.node_id === selected)) selected = state.rooms[0]?.node_id || null;
    const live = state.mode === "live";
    $("mode-banner").classList.toggle("live", live);
    $("mode-banner").textContent = live ? "LIVE MODE · Only readings received from configured sensors appear here." : "SIMULATED DATA · Preview only. No sensor connection. Live receiver is disabled.";
    $("footer-mode").textContent = live ? "Live sensors" : "Simulated preview";
    $("retention").textContent = `${state.retention_days} day retention · stored on this device`;
    $("connection").hidden = true;
    $("summary").textContent = `${state.rooms.length} rooms · ${state.rooms.filter(room=>room.status==="fresh").length} reporting now`;
    $("refresh").textContent = "Updates every 10 seconds";
    document.querySelectorAll("[data-hours]").forEach(button => { button.disabled = Number(button.dataset.hours) > state.retention_days * 24; });
    if (hours > state.retention_days * 24) hours = Math.min(1, state.retention_days * 24);
    document.querySelectorAll("[data-hours]").forEach(button => button.setAttribute("aria-pressed", String(Number(button.dataset.hours) === hours)));
    renderRooms(); await fetchHistory();
  } catch (_) {
    failed = true;
    $("connection").hidden = false;
    $("connection").textContent = `Collector unreachable. Displaying cached values${lastSuccess ? ` from ${new Date(lastSuccess).toLocaleTimeString()}` : " if available"}. Reconnecting automatically.`;
    $("summary").textContent = "Collector connection lost · values are not current";
    $("refresh").textContent = "Reconnecting…";
    renderRooms();
  } finally { window.setTimeout(refresh, 10000); }
}

function setUnit(next) {
  unit = next;
  try { localStorage.setItem("roomlight.unit", unit); } catch (_) {}
  $("celsius").setAttribute("aria-pressed", String(unit === "C"));
  $("fahrenheit").setAttribute("aria-pressed", String(unit === "F"));
  renderRooms(); renderChart();
}
$("celsius").addEventListener("click",()=>setUnit("C"));
$("fahrenheit").addEventListener("click",()=>setUnit("F"));
document.querySelectorAll("[data-hours]").forEach(button => button.addEventListener("click",()=>{
  hours = Number(button.dataset.hours); history = null;
  document.querySelectorAll("[data-hours]").forEach(b=>b.setAttribute("aria-pressed",String(b===button)));
  renderChart(); fetchHistory();
}));
$("timezone").textContent = Intl.DateTimeFormat().resolvedOptions().timeZone;
function clock() { $("clock").textContent = new Date().toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"}); }
clock(); window.setInterval(clock, 1000); setUnit(unit); refresh();
new ResizeObserver(() => renderChart()).observe($("chart-wrap"));
