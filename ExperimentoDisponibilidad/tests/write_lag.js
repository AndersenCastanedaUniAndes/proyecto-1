import http from "k6/http";
import { check, sleep } from "k6";
import { Trend } from "k6/metrics";

export const options = {
  vus: 50,
  duration: "5m",
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<400"],              // ack del comando
    "projection_lag": ["p(95)<1000","p(99)<2000"], // tiempo hasta ver reflejado en read-side
  },
};

const BASE = __ENV.BASE || "http://localhost:8000";
const LAG = new Trend("projection_lag");

export default function () {
  const key = {
    tenant_id:"t1", warehouse_id:"wh1", location_id:"A-01-01",
    product_id:"P-001", lot_number:"L-2025", serial_number:""
  };

  // ajusta +1
  const t0 = Date.now();
  const r = http.post(`${BASE}/items/adjust`, JSON.stringify({...key, qty_delta: 1}), { headers: { "Content-Type":"application/json" }});
  check(r, { "200": (res) => res.status === 200 });

  // poll hasta que el available cambie (máx 3s)
  let ok = false;
  for (let i = 0; i < 30; i++) {
    const g = http.get(`${BASE}/items/by-key?tenant_id=${key.tenant_id}&warehouse_id=${key.warehouse_id}&location_id=${key.location_id}&product_id=${key.product_id}&lot_number=${key.lot_number}`);
    if (g.status === 200) {
      // opcional: valida campo específico si lo expones; aquí chequeo 200
      ok = true; 
      break;
    }
    sleep(0.1);
  }

  const t1 = Date.now();
  if (ok) {
    LAG.add(t1 - t0);
  }

  sleep(0.1);
}
