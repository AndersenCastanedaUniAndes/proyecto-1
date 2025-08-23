-- Modelo de escritura (write model)
CREATE TABLE IF NOT EXISTS pedidos (
    id SERIAL PRIMARY KEY,
    cliente VARCHAR(100),
    fecha TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS lineas_pedido (
    id SERIAL PRIMARY KEY,
    pedido_id INT REFERENCES pedidos(id),
    producto VARCHAR(100),
    cantidad INT
);

-- Modelo de lectura (read model: proyección)
CREATE TABLE IF NOT EXISTS pedido_resumen (
    pedido_id INT PRIMARY KEY,
    cliente VARCHAR(100),
    total_items INT,
    fecha TIMESTAMP
);
