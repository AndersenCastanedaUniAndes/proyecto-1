import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  vus: 50,
  duration: "5m",
  thresholds: {
    http_req_failed: ["rate<0.005"],
    http_req_duration: ["p(95)<1000","p(99)<2000"],
  },
};

const BASE = __ENV.BASE || "http://localhost:8000";

export default function () {
  const r = http.get(`${BASE}/items?tenant_id=t1&warehouse_id=wh1`);
  check(r, { "200": (res) => res.status === 200 });
  sleep(0.1);
}
