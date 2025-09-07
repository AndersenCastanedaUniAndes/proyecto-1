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


const TENANTS       = ["t1","t2","t3","t4","t5","t6","t7","t8","t9","t10"];
const WHEREHOUSE    = ["wh1","wh2","wh3","wh4","wh5","wh6","wh7","wh8","wh9","wh10"];
const LOCATIONS     = ["A-01-01","A-01-02","A-01-03","A-01-04","A-01-05","A-01-06","A-01-07","A-01-08","A-01-09","A-01-10"];
const PRODUCTS      = ["P-001","P-002","P-003","P-004","P-005","P-006","P-007","P-008","P-009","P-010"];
const STORAGE_CLASS = ["Ambient","Refrigerated","Frozen"];
const SERIAL_NUMBER = ["S-001","S-002","S-003","S-004","S-005","S-006","S-007","S-008","S-009","S-010"];
const QUANTITY      = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
const RESERVED      = [1, 2, 3, 4, 5];

export default function () {
  // random item
  let payload = {
    "tenant_id"     : TENANTS[Math.floor(Math.random() * TENANTS.length)],
    "warehouse_id"  : WHEREHOUSE[Math.floor(Math.random() * WHEREHOUSE.length)],
    "location_id"   : LOCATIONS[Math.floor(Math.random() * LOCATIONS.length)],
    "product_id"    : PRODUCTS[Math.floor(Math.random() * PRODUCTS.length)],
    "lot_number"    : "L-2025",
    "serial_number" : SERIAL_NUMBER[Math.floor(Math.random() * SERIAL_NUMBER.length)],
    "qty_on_hand"   : QUANTITY[Math.floor(Math.random() * QUANTITY.length)],
    "qty_reserved"  : RESERVED[Math.floor(Math.random() * RESERVED.length)],
    "storage_class" : STORAGE_CLASS[Math.floor(Math.random() * STORAGE_CLASS.length)]
};

  // ajusta +1
  const post = http.post(`${BASE}/items/upsert`, JSON.stringify(payload), { headers: { "Content-Type":"application/json" }});
  check(post, { "200": (res) => res.status === 200 });

  sleep(0.1);
}
