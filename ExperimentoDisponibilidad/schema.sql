-- =========================
-- WRITE-SIDE (fuente de verdad)
-- =========================

-- Inventario por ubicación + lote/serie (PK compuesta)
CREATE TABLE IF NOT EXISTS inventory_item (
  tenant_id             TEXT NOT NULL,
  warehouse_id          TEXT NOT NULL,
  location_id           TEXT NOT NULL,
  product_id            TEXT NOT NULL,
  lot_number            TEXT NOT NULL DEFAULT '',
  serial_number         TEXT NOT NULL DEFAULT '',
  uom                   TEXT NOT NULL DEFAULT 'unit',
  qty_on_hand           INTEGER NOT NULL DEFAULT 0,
  qty_reserved          INTEGER NOT NULL DEFAULT 0,
  quality_status        TEXT NOT NULL DEFAULT 'Available',   -- Available|Quarantine|Damaged|Expired|Hold
  storage_class         TEXT NOT NULL DEFAULT 'Ambient',     -- Ambient|2_8C|Minus20C|Minus80C|Hazmat|Controlled
  temp_min_c            NUMERIC,
  temp_max_c            NUMERIC,
  last_temp_c           NUMERIC,
  last_temp_ts          TIMESTAMPTZ,
  cold_chain_status     TEXT,                               -- OK|Excursion|Unknown
  excursions_count      INT NOT NULL DEFAULT 0,
  mfg_date              DATE,
  expiry_date           DATE,
  country_of_origin     TEXT,
  gs1_gtin              TEXT,
  regulatory_cert_id    TEXT,
  created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
  row_version           BIGINT NOT NULL DEFAULT 0,
  is_active             BOOLEAN NOT NULL DEFAULT TRUE,
  PRIMARY KEY (tenant_id, warehouse_id, location_id, product_id, lot_number, serial_number)
);

-- Índices de consulta más comunes
CREATE INDEX IF NOT EXISTS inv_item_idx_prod
  ON inventory_item(tenant_id, product_id);

CREATE INDEX IF NOT EXISTS inv_item_idx_exp
  ON inventory_item(tenant_id, warehouse_id, expiry_date);

CREATE INDEX IF NOT EXISTS inv_item_idx_loc
  ON inventory_item(tenant_id, warehouse_id, location_id);

CREATE INDEX IF NOT EXISTS inv_item_idx_storage
  ON inventory_item(tenant_id, warehouse_id, storage_class, product_id);

-- Ledger inmutable de movimientos (auditoría e idempotencia)
CREATE TABLE IF NOT EXISTS inventory_tx (
  tx_id           BIGSERIAL PRIMARY KEY,
  event_id        UUID NOT NULL UNIQUE,                 -- para idempotencia
  tenant_id       TEXT NOT NULL,
  warehouse_id    TEXT NOT NULL,
  location_id     TEXT NOT NULL,
  product_id      TEXT NOT NULL,
  lot_number      TEXT NOT NULL DEFAULT '',
  serial_number   TEXT NOT NULL DEFAULT '',
  tx_type         TEXT NOT NULL,                        -- Receipt|MoveOut|MoveIn|Pick|Adjust|Reserve|Release|Dispose
  qty_delta       INTEGER NOT NULL DEFAULT 0,
  reason          TEXT,
  evidence_url    TEXT,
  performed_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  performed_by    TEXT
);

-- =========================
-- READ-SIDE (denormalizado)
-- =========================
CREATE TABLE IF NOT EXISTS inventory_search (
  tenant_id         TEXT NOT NULL,
  warehouse_id      TEXT NOT NULL,
  location_id       TEXT NOT NULL,
  product_id        TEXT NOT NULL,
  lot_number        TEXT NOT NULL DEFAULT '',
  serial_number     TEXT NOT NULL DEFAULT '',
  product_sku       TEXT,
  product_name      TEXT,
  manufacturer_id   TEXT,
  manufacturer_name TEXT,
  qty_on_hand       INTEGER NOT NULL DEFAULT 0,
  qty_reserved      INTEGER NOT NULL DEFAULT 0,
  qty_available     INTEGER NOT NULL DEFAULT 0,
  storage_class     TEXT,
  expiry_date       DATE,
  last_temp_c       NUMERIC,
  last_temp_ts      TIMESTAMPTZ,
  quality_status    TEXT,
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (tenant_id, warehouse_id, location_id, product_id, lot_number, serial_number)
);

CREATE INDEX IF NOT EXISTS inv_search_idx_product
  ON inventory_search(tenant_id, product_id);

CREATE INDEX IF NOT EXISTS inv_search_idx_exp
  ON inventory_search(tenant_id, warehouse_id, expiry_date);

CREATE INDEX IF NOT EXISTS inv_search_idx_loc
  ON inventory_search(tenant_id, warehouse_id, location_id);

-- Eventos ya procesados por el proyector (para no duplicar)
CREATE TABLE IF NOT EXISTS processed_events (
  event_id  UUID PRIMARY KEY,
  processed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
