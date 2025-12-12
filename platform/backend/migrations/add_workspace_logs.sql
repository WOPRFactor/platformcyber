-- Migración: Agregar tabla workspace_logs y campo status a workspaces
-- Fecha: 2025-11-26
-- Descripción: Crea tabla para persistencia de logs por workspace y agrega campo status

-- ============================================
-- 1. AGREGAR CAMPO STATUS A WORKSPACES
-- ============================================

-- Agregar columna status (compatible con SQLite y PostgreSQL)
-- SQLite no soporta ENUM nativo, usamos VARCHAR
-- PostgreSQL puede usar CHECK constraint para validar valores

-- Para SQLite
ALTER TABLE workspaces ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active';

-- Para PostgreSQL (si es necesario, ejecutar después)
-- ALTER TABLE workspaces ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active';
-- ALTER TABLE workspaces ADD CONSTRAINT check_workspace_status 
--   CHECK (status IN ('active', 'paused', 'archived', 'completed'));

-- Actualizar workspaces existentes: si is_active=true -> 'active', si is_active=false -> 'archived'
UPDATE workspaces SET status = CASE 
  WHEN is_active = 1 THEN 'active'
  ELSE 'archived'
END WHERE status IS NULL;

-- ============================================
-- 2. CREAR TABLA WORKSPACE_LOGS
-- ============================================

CREATE TABLE IF NOT EXISTS workspace_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- SQLite
    -- id SERIAL PRIMARY KEY,  -- PostgreSQL (usar esta línea en PostgreSQL)
    
    workspace_id INTEGER NOT NULL,
    source VARCHAR(50) NOT NULL,  -- BACKEND, CELERY, NIKTO, NMAP, etc.
    level VARCHAR(10) NOT NULL,   -- DEBUG, INFO, WARNING, ERROR
    message TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    
    -- Campos opcionales
    task_id VARCHAR(100),          -- ID de tarea Celery
    log_metadata TEXT,            -- JSON con info adicional (metadata es reservado en SQLAlchemy)
    
    -- Foreign key con CASCADE DELETE
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
);

-- ============================================
-- 3. CREAR ÍNDICES PARA PERFORMANCE
-- ============================================

-- Índice en workspace_id (más usado en queries)
CREATE INDEX IF NOT EXISTS idx_workspace_logs_workspace_id 
    ON workspace_logs(workspace_id);

-- Índice en timestamp (para ordenamiento y filtros por fecha)
CREATE INDEX IF NOT EXISTS idx_workspace_logs_timestamp 
    ON workspace_logs(timestamp);

-- Índice compuesto (workspace_id + timestamp) para queries comunes
CREATE INDEX IF NOT EXISTS idx_workspace_logs_workspace_timestamp 
    ON workspace_logs(workspace_id, timestamp);

-- Índice en source (para filtros por fuente)
CREATE INDEX IF NOT EXISTS idx_workspace_logs_source 
    ON workspace_logs(source);

-- Índice en level (para filtros por nivel)
CREATE INDEX IF NOT EXISTS idx_workspace_logs_level 
    ON workspace_logs(level);

-- Índice en status de workspaces (para filtros)
CREATE INDEX IF NOT EXISTS idx_workspaces_status 
    ON workspaces(status);

-- ============================================
-- 4. COMENTARIOS (PostgreSQL)
-- ============================================

-- Para PostgreSQL, agregar comentarios:
-- COMMENT ON TABLE workspace_logs IS 'Logs persistentes por workspace';
-- COMMENT ON COLUMN workspace_logs.workspace_id IS 'ID del workspace (FK)';
-- COMMENT ON COLUMN workspace_logs.source IS 'Fuente del log: BACKEND, CELERY, NIKTO, etc.';
-- COMMENT ON COLUMN workspace_logs.level IS 'Nivel: DEBUG, INFO, WARNING, ERROR';
-- COMMENT ON COLUMN workspace_logs.message IS 'Mensaje del log (sanitizado)';
-- COMMENT ON COLUMN workspace_logs.timestamp IS 'Timestamp con microsegundos';
-- COMMENT ON COLUMN workspace_logs.task_id IS 'ID de tarea Celery (opcional)';
-- COMMENT ON COLUMN workspace_logs.metadata IS 'JSON con información adicional';

