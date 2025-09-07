from db import fetch

async def listar_items(tenant_id: str, warehouse_id: str):
    return await fetch(
        """
        SELECT * FROM inventory_search
        WHERE tenant_id=$1 AND warehouse_id=$2
        ORDER BY expiry_date NULLS LAST, product_id
        """,
        tenant_id, warehouse_id
    )

async def obtener_item(key):
    rows = await fetch(
        """
        SELECT * FROM inventory_item
        WHERE tenant_id=$1 AND warehouse_id=$2 AND location_id=$3 AND product_id=$4
        AND lot_number=COALESCE($5,'') AND serial_number=COALESCE($6,'')
        """,
        key.tenant_id, key.warehouse_id, key.location_id, key.product_id, key.lot_number, key.serial_number
    )
    return rows[0] if rows else None
