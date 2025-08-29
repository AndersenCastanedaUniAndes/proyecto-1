from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date

class ItemKey(BaseModel):
    tenant_id: str
    warehouse_id: str
    location_id: str
    product_id: str
    lot_number: Optional[str] = Field(default="")
    serial_number: Optional[str] = Field(default="")

class ItemUpsert(ItemKey):
    uom: str = "unit"
    qty_on_hand: int = 0
    qty_reserved: int = 0
    quality_status: str = "Available"
    storage_class: str = "Ambient"
    temp_min_c: Optional[float] = None
    temp_max_c: Optional[float] = None
    mfg_date: Optional[date] = None
    expiry_date: Optional[date] = None
    country_of_origin: Optional[str] = None
    gs1_gtin: Optional[str] = None
    regulatory_cert_id: Optional[str] = None

class StockAdjust(ItemKey):
    qty_delta: int
    reason: Optional[str] = None

class StockReserve(ItemKey):
    qty_to_reserve: int
    reason: Optional[str] = None

class ItemResponse(ItemKey):
    qty_on_hand: int
    qty_reserved: int
    qty_available: int
    storage_class: str
    expiry_date: Optional[date] = None
    quality_status: str
    updated_at: datetime
