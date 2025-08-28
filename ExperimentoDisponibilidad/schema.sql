-- Modelo de escritura (write model)
CREATE TABLE IF NOT EXISTS inventario (
    id SERIAL PRIMARY KEY,
    cliente VARCHAR(100),
    fecha_caducidad TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS lineas_inventario (
    id SERIAL PRIMARY KEY,
    inventario_id INT REFERENCES inventario(id),
    nombre VARCHAR(100),
    cantidad INT
);

-- Índice para acelerar búsquedas por inventario en las líneas
CREATE INDEX IF NOT EXISTS idx_lineas_inventario_inventario_id ON lineas_inventario(inventario_id);

-- Modelo de lectura (read model: proyección)
CREATE TABLE IF NOT EXISTS inventario_resumen (
    inventario_id INT PRIMARY KEY,
    cliente VARCHAR(100),
    total_items INT,
    fecha_caducidad TIMESTAMP
);

-- Índice para orden por fecha_caducidad (ya que se usa ORDER BY fecha_caducidad DESC)
CREATE INDEX IF NOT EXISTS idx_inventario_resumen_fecha_caducidad ON inventario_resumen(fecha_caducidad DESC);
