-- Script de inicialización para PostgreSQL
-- Crear base de datos si no existe
CREATE DATABASE IF NOT EXISTS experimento_seguridad;

-- Usar la base de datos
\c experimento_seguridad;

-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Comentarios sobre el esquema
COMMENT ON DATABASE experimento_seguridad IS 'Base de datos para experimento de seguridad JWT + RBAC';
