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

const Product = {
  tenant_id:"t1", warehouse_id:"wh1", location_id:"A-01-01",
  product_id:"P-001", lot_number:"L-2025", serial_number:"", qty_delta: 1
};

export default function () {
  const t0 = Date.now();

  // Agrega +1 al item en inventario
  const pr = http.post(`${BASE}/items/adjust`, JSON.stringify(Product), { headers: { "Content-Type":"application/json" }});
  check(pr, { "200": (res) => res.status === 200 });

  // Check por 3 segundos si el GET refleja el cambio
  let ok = false;
  for (let i = 0; i < 30; i++) {
    const gr = http.get(`${BASE}/items/by-key?tenant_id=${Product.tenant_id}&warehouse_id=${Product.warehouse_id}&location_id=${Product.location_id}&product_id=${Product.product_id}&lot_number=${Product.lot_number}`);

    // Valida si el request GET es exitoso y las tablas de escritura y lectura están sincronizadas
    if (gr.status === 200 && pr.json().qty_available === gr.json().qty_available) {
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
