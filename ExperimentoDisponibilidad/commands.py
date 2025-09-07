from datetime import datetime
import logging
from uuid import UUID, uuid4

from actions import ITEM_UPSERTED, ITEM_ADJUSTED, ITEM_RESERVED, ITEM_RELEASED
import db
from events import publish_event
from unit_of_work import UnitOfWork
from models import ItemUpsert, ItemResponse

log = logging.getLogger(__name__)

KEY_COLUMNS = [
    "tenant_id",
    "warehouse_id",
    "location_id",
    "product_id",
    "lot_number",
    "serial_number"
]

KEY_COLS = ", ".join(KEY_COLUMNS)

async def upsert_item(data: ItemUpsert) -> ItemResponse:
    async with UnitOfWork(db.pool) as conn:
        write_row = await conn.fetchrow(
            f"""
                INSERT INTO inventory_item(
                    {KEY_COLS},
                    uom, qty_on_hand, qty_reserved,
                    quality_status, storage_class,
                    temp_min_c, temp_max_c,
                    mfg_date, expiry_date,
                    country_of_origin, gs1_gtin, regulatory_cert_id,
                    created_at, updated_at, row_version,
                    is_active
                )
                VALUES (
                    $1,$2,$3,$4, COALESCE($5,''), COALESCE($6,''),  -- KEY_COLUMNS
                    $7,$8,$9,                                       -- uom, qty_on_hand, qty_reserved
                    $10,$11,                                        -- quality_status, storage_class
                    $12,$13,                                        -- temp_min_c, temp_max_c
                    $14,$15,                                        -- mfg_date, expiry_date
                    $16,$17,$18,                                    -- country_of_origin, gs1_gtin, regulatory_cert_id
                    $19,$20,$21,                                    -- created_at, updated_at, row_version
                    TRUE                                            -- is_active
                )
                ON CONFLICT (tenant_id, warehouse_id, location_id, product_id, lot_number, serial_number)
                DO UPDATE SET
                    uom=EXCLUDED.uom,
                    qty_on_hand=EXCLUDED.qty_on_hand,
                    qty_reserved=EXCLUDED.qty_reserved,
                    quality_status=EXCLUDED.quality_status,
                    storage_class=EXCLUDED.storage_class,
                    temp_min_c=EXCLUDED.temp_min_c,
                    temp_max_c=EXCLUDED.temp_max_c,
                    mfg_date=EXCLUDED.mfg_date,
                    expiry_date=EXCLUDED.expiry_date,
                    country_of_origin=EXCLUDED.country_of_origin,
                    gs1_gtin=EXCLUDED.gs1_gtin,
                    regulatory_cert_id=EXCLUDED.regulatory_cert_id,
                    updated_at=now(),
                    row_version=inventory_item.row_version + 1
                RETURNING tenant_id, warehouse_id, location_id, product_id, lot_number, serial_number,
                        qty_on_hand, qty_reserved, quality_status, storage_class, expiry_date, updated_at
            """,
            data.tenant_id, data.warehouse_id, data.location_id, data.product_id, data.lot_number, data.serial_number,  # KEY_COLUMNS
            data.uom, data.qty_on_hand, data.qty_reserved,                                                              # uom, qty_on_hand, qty_reserved
            data.quality_status, data.storage_class,                                                                    # quality_status, storage_class
            data.temp_min_c, data.temp_max_c,                                                                           # temp_min_c, temp_max_c
            data.mfg_date, data.expiry_date,                                                                            # mfg_date, expiry_date
            data.country_of_origin, data.gs1_gtin, data.regulatory_cert_id,                                             # country_of_origin, gs1_gtin, regulatory_cert_id
            datetime.utcnow(), datetime.utcnow(), 0                                                                     # created_at, updated_at, row_version
        )

        qty_available = int(write_row["qty_on_hand"]) - int(write_row["qty_reserved"])
        updated_at = write_row["updated_at"]

        await conn.execute(
            """
                INSERT INTO inventory_search
                    (tenant_id, warehouse_id, location_id, product_id, lot_number, serial_number,
                    qty_on_hand, qty_reserved, qty_available, storage_class, expiry_date, quality_status, updated_at)
                VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)
                ON CONFLICT (tenant_id, warehouse_id, location_id, product_id, lot_number, serial_number)
                DO UPDATE SET
                    qty_on_hand=excluded.qty_on_hand,
                    qty_reserved=excluded.qty_reserved,
                    qty_available=excluded.qty_available,
                    storage_class=excluded.storage_class,
                    expiry_date=excluded.expiry_date,
                    quality_status=excluded.quality_status,
                    updated_at=excluded.updated_at
            """,
            data.tenant_id, data.warehouse_id, data.location_id, data.product_id, data.lot_number, data.serial_number,
            data.qty_on_hand, data.qty_reserved, qty_available, data.storage_class, data.expiry_date, data.quality_status, updated_at
        )

        return ItemResponse(
            tenant_id      = write_row["tenant_id"],
            warehouse_id   = write_row["warehouse_id"],
            location_id    = write_row["location_id"],
            product_id     = write_row["product_id"],
            lot_number     = write_row["lot_number"],
            serial_number  = write_row["serial_number"],
            qty_on_hand    = int(write_row["qty_on_hand"]),
            qty_reserved   = int(write_row["qty_reserved"]),
            qty_available  = qty_available,
            storage_class  = write_row["storage_class"],
            expiry_date    = write_row["expiry_date"],
            quality_status = write_row["quality_status"],
            updated_at     = updated_at
        )

async def adjust_stock(data):
    async with UnitOfWork(db.pool) as conn:
        row = await conn.fetchrow(
            f"""
            UPDATE inventory_item
            SET qty_on_hand = qty_on_hand + $7,
                updated_at = now(),
                row_version = row_version + 1
            WHERE tenant_id=$1 AND warehouse_id=$2 AND location_id=$3 AND product_id=$4
            AND lot_number=COALESCE($5,'') AND serial_number=COALESCE($6,'')
            RETURNING tenant_id, warehouse_id, location_id, product_id, lot_number, serial_number,
                qty_on_hand, qty_reserved, quality_status, storage_class, expiry_date, updated_at
            """,
            data.tenant_id, data.warehouse_id, data.location_id, data.product_id, data.lot_number, data.serial_number, data.qty_delta
        )

        qty_available = int(row["qty_on_hand"]) - int(row["qty_reserved"])
        await conn.execute(
            """
            INSERT INTO inventory_search
                (tenant_id, warehouse_id, location_id, product_id, lot_number, serial_number,
                qty_on_hand, qty_reserved, qty_available, storage_class, expiry_date, quality_status, updated_at)
            VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)
            ON CONFLICT (tenant_id, warehouse_id, location_id, product_id, lot_number, serial_number)
            DO UPDATE SET
                qty_on_hand=excluded.qty_on_hand,
                qty_reserved=excluded.qty_reserved,
                qty_available=excluded.qty_available,
                storage_class=excluded.storage_class,
                expiry_date=excluded.expiry_date,
                quality_status=excluded.quality_status,
                updated_at=excluded.updated_at
            """,
            row["tenant_id"], row["warehouse_id"], row["location_id"], row["product_id"], row["lot_number"], row["serial_number"],
            row["qty_on_hand"], row["qty_reserved"], qty_available, row["storage_class"], row["expiry_date"], row["quality_status"], row["updated_at"]
        )

        return ItemResponse(
            tenant_id      = row["tenant_id"],
            warehouse_id   = row["warehouse_id"],
            location_id    = row["location_id"],
            product_id     = row["product_id"],
            lot_number     = row["lot_number"],
            serial_number  = row["serial_number"],
            qty_on_hand    = int(row["qty_on_hand"]),
            qty_reserved   = int(row["qty_reserved"]),
            qty_available  = qty_available,
            storage_class  = row["storage_class"],
            expiry_date    = row["expiry_date"],
            quality_status = row["quality_status"],
            updated_at     = row["updated_at"]
        )

async def reserve_stock(data):
    async with UnitOfWork(db.pool) as conn:
        # reserva (aumenta qty_reserved)
        await conn.execute(f"""
            UPDATE inventory_item
            SET qty_reserved = GREATEST(0, qty_reserved + $7),
                updated_at = now(),
                row_version = row_version + 1
            WHERE tenant_id=$1 AND warehouse_id=$2 AND location_id=$3 AND product_id=$4
            AND lot_number=COALESCE($5,'') AND serial_number=COALESCE($6,'')
        """, data.tenant_id, data.warehouse_id, data.location_id, data.product_id, data.lot_number, data.serial_number, data.qty_to_reserve)

        await publish_event(ITEM_RESERVED, {
            "tenant_id"      : data.tenant_id,
            "warehouse_id"   : data.warehouse_id,
            "location_id"    : data.location_id,
            "product_id"     : data.product_id,
            "lot_number"     : data.lot_number or "",
            "serial_number"  : data.serial_number or "",
            "qty_to_reserve" : data.qty_to_reserve
        })
