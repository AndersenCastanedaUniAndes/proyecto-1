import http from "k6/http";
import { check, sleep } from "k6";
import { Trend } from "k6/metrics";
import exec from "k6/execution";

// --- Config ---
const BASE = __ENV.BASE || "http://localhost:8000";

// Tamaños del espacio de claves (deben coincidir con tu seed)
const TENANTS = parseInt(__ENV.TENANTS || "1", 10);
const WAREHOUSES = parseInt(__ENV.WAREHOUSES || "2", 10);
const PRODUCTS = parseInt(__ENV.PRODUCTS || "80", 10);
const LOTS = parseInt(__ENV.LOTS || "3", 10);

// Métrica de lag (filtrable por escenario)
const LAG = new Trend("projection_lag");

// Escenarios y SLOs
export const options = {
  scenarios: {
    readers: {
      executor: "constant-arrival-rate",
      rate: parseInt(__ENV.READ_RPS || "200", 10), // lecturas por segundo
      timeUnit: "1s",
      duration: __ENV.DURATION || "10m",
      preAllocatedVUs: 50,
      maxVUs: 200,
      exec: "readScenario",
    },
    writers: {
      executor: "constant-arrival-rate",
      rate: parseInt(__ENV.WRITE_RPS || "50", 10), // escrituras por segundo
      timeUnit: "1s",
      duration: __ENV.DURATION || "10m",
      preAllocatedVUs: 20,
      maxVUs: 100,
      exec: "writeScenario",
    },
  },
  thresholds: {
    "http_req_failed{scenario:readers}": ["rate<0.005"],
    "http_req_duration{scenario:readers}": ["p(95)<1000", "p(99)<2000"],
    "http_req_failed{scenario:writers}": ["rate<0.01"],
    "http_req_duration{scenario:writers}": ["p(95)<400"],
    "projection_lag{scenario:writers}": ["p(95)<1000", "p(99)<2000"],
  },
};

// ----------------- helpers -----------------
function pad(n, w = 4) {
  return String(n).padStart(w, "0");
}

function makeKey() {
  const vu = exec.vu.idInInstance;              // 1..N
  const it = exec.scenario.iterationInInstance; // 0..∞
  const t = 1 + (vu % TENANTS);
  const w = 1 + (it % WAREHOUSES);
  const p = 1 + ((vu + it) % PRODUCTS);
  const l = 1 + ((vu + it) % LOTS);
  const year = new Date().getFullYear();
  // ubicación sintética (coincide con patrones de seed)
  const rack = pad(1 + ((vu + it) % 50), 2);
  const level = pad(1 + ((vu + it) % 10), 2);
  const loc = `A-${rack}-${level}`;

  return {
    tenant_id: `t${t}`,
    warehouse_id: `wh${w}`,
    location_id: loc,
    product_id: `P-${pad(p)}`,
    lot_number: `L-${year}-${pad(p)}-${l}`,
    serial_number: "",
  };
}

function getByKey(k) {
  const url = `${BASE}/items/by-key?tenant_id=${k.tenant_id}&warehouse_id=${k.warehouse_id}&location_id=${k.location_id}&product_id=${k.product_id}&lot_number=${k.lot_number}`;
  return http.get(url);
}

// ----------------- escenarios -----------------
export function readScenario() {
  // 80–90% de las lecturas será /items por almacén; el resto podría alternar by-key
  const tenant = `t${1 + (exec.vu.idInInstance % TENANTS)}`;
  const wh = `wh${1 + (exec.scenario.iterationInInstance % WAREHOUSES)}`;

  const r = http.get(`${BASE}/items?tenant_id=${tenant}&warehouse_id=${wh}`);
  check(r, { "200": (res) => res.status === 200 });

  sleep(0.05);
}

export function writeScenario() {
  const k = makeKey();

  // 1) baseline (para medir cambio real)
  let before = getByKey(k);
  if (before.status === 404) {
    // fallback opcional: si no existe, intenta crearlo con upsert mínimo
    const up = http.post(`${BASE}/items/upsert`, JSON.stringify({
      ...k, uom: "unit", qty_on_hand: 0, qty_reserved: 0,
      quality_status: "Available", storage_class: "Ambient"
    }), { headers: { "Content-Type": "application/json" }});
    check(up, { "upsert 2xx": (res) => res.status >= 200 && res.status < 300 });
    before = getByKey(k);
  }
  let beforeBody = {};
  if (before.status === 200) {
    try { beforeBody = before.json(); } catch (_) {}
  }

  const baseQty = Number(beforeBody.qty_on_hand || 0);
  const baseUpdated = String(beforeBody.updated_at || "");

  // 2) comando de ajuste (+1 o -1)
  const delta = Math.random() < 0.5 ? 1 : -1;
  const t0 = Date.now();
  const adj = http.post(`${BASE}/items/adjust`, JSON.stringify({ ...k, qty_delta: delta }), {
    headers: { "Content-Type": "application/json" },
  });
  check(adj, { "adjust 2xx": (res) => res.status >= 200 && res.status < 300 });

  // 3) poll read-side hasta ver el cambio (máx 3s)
  let ok = false;
  for (let i = 0; i < 30; i++) {
    const g = getByKey(k);
    if (g.status === 200) {
      let jb = {};
      try { jb = g.json(); } catch (_) {}
      const qty = Number(jb.qty_on_hand || 0);
      const upd = String(jb.updated_at || "");
      if (qty === baseQty + delta || upd !== baseUpdated) {
        ok = true;
        break;
      }
    }
    sleep(0.1);
  }

  const t1 = Date.now();
  if (ok) {
    // etiqueta por escenario para thresholds filtrados
    LAG.add(t1 - t0, { scenario: exec.scenario.name });
  }

  sleep(0.05);
}
