-- Migración: Agregar campos de target y scope a workspaces
-- Fecha: 2025-11-24
-- Descripción: Agrega campos para target principal, scope y fechas del proyecto

-- Agregar columnas de target
ALTER TABLE workspaces ADD COLUMN IF NOT EXISTS target_domain VARCHAR(255);
ALTER TABLE workspaces ADD COLUMN IF NOT EXISTS target_ip VARCHAR(50);
ALTER TABLE workspaces ADD COLUMN IF NOT EXISTS target_type VARCHAR(50);

-- Agregar columnas de scope
ALTER TABLE workspaces ADD COLUMN IF NOT EXISTS in_scope TEXT;
ALTER TABLE workspaces ADD COLUMN IF NOT EXISTS out_of_scope TEXT;

-- Agregar fechas del proyecto
ALTER TABLE workspaces ADD COLUMN IF NOT EXISTS start_date DATE;
ALTER TABLE workspaces ADD COLUMN IF NOT EXISTS end_date DATE;

-- Agregar notas adicionales
ALTER TABLE workspaces ADD COLUMN IF NOT EXISTS notes TEXT;

-- Crear índice para búsqueda por target_domain
CREATE INDEX IF NOT EXISTS idx_workspaces_target_domain ON workspaces(target_domain);

-- Crear índice para búsqueda por target_type
CREATE INDEX IF NOT EXISTS idx_workspaces_target_type ON workspaces(target_type);

-- Comentarios
COMMENT ON COLUMN workspaces.target_domain IS 'Dominio o URL principal del target';
COMMENT ON COLUMN workspaces.target_ip IS 'Dirección IP del target (opcional)';
COMMENT ON COLUMN workspaces.target_type IS 'Tipo de aplicación: web, api, mobile, network, other';
COMMENT ON COLUMN workspaces.in_scope IS 'Elementos dentro del alcance del proyecto';
COMMENT ON COLUMN workspaces.out_of_scope IS 'Elementos fuera del alcance del proyecto';
COMMENT ON COLUMN workspaces.start_date IS 'Fecha de inicio del proyecto';
COMMENT ON COLUMN workspaces.end_date IS 'Fecha límite del proyecto';
COMMENT ON COLUMN workspaces.notes IS 'Notas adicionales del proyecto';




