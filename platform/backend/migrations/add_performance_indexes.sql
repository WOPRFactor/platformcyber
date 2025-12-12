-- Performance Optimization - Database Indexes
-- =============================================
-- Fecha: 23 Noviembre 2025
-- Descripción: Agregar índices para mejorar performance de queries comunes

-- ============================================
-- USERS TABLE
-- ============================================

-- Index para búsqueda por email (login)
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Index para búsqueda por username (login)
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Index para filtrar usuarios activos
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- Index para búsqueda por rol
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- ============================================
-- WORKSPACES TABLE
-- ============================================

-- Index para filtrar por user_id (mis workspaces)
CREATE INDEX IF NOT EXISTS idx_workspaces_user_id ON workspaces(user_id);

-- Index para ordenar por created_at
CREATE INDEX IF NOT EXISTS idx_workspaces_created_at ON workspaces(created_at DESC);

-- Index compuesto para filtrar workspaces activos de un usuario
CREATE INDEX IF NOT EXISTS idx_workspaces_user_active ON workspaces(user_id, is_active);

-- ============================================
-- SCANS TABLE
-- ============================================

-- Index para filtrar scans por workspace
CREATE INDEX IF NOT EXISTS idx_scans_workspace_id ON scans(workspace_id);

-- Index para filtrar por tipo de scan
CREATE INDEX IF NOT EXISTS idx_scans_scan_type ON scans(scan_type);

-- Index para filtrar por status
CREATE INDEX IF NOT EXISTS idx_scans_status ON scans(status);

-- Index para ordenar por fecha
CREATE INDEX IF NOT EXISTS idx_scans_created_at ON scans(created_at DESC);

-- Index compuesto para queries comunes (workspace + status)
CREATE INDEX IF NOT EXISTS idx_scans_workspace_status ON scans(workspace_id, status);

-- Index compuesto para queries de scans activos
CREATE INDEX IF NOT EXISTS idx_scans_workspace_active ON scans(workspace_id, status) WHERE status IN ('running', 'pending');

-- ============================================
-- SCAN_RESULTS TABLE
-- ============================================

-- Index para obtener resultados de un scan
CREATE INDEX IF NOT EXISTS idx_scan_results_scan_id ON scan_results(scan_id);

-- Index para filtrar por tipo de resultado
CREATE INDEX IF NOT EXISTS idx_scan_results_result_type ON scan_results(result_type);

-- Index para ordenar por timestamp
CREATE INDEX IF NOT EXISTS idx_scan_results_timestamp ON scan_results(timestamp DESC);

-- Index compuesto scan + tipo
CREATE INDEX IF NOT EXISTS idx_scan_results_scan_type ON scan_results(scan_id, result_type);

-- ============================================
-- VULNERABILITIES TABLE
-- ============================================

-- Index para filtrar por workspace
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_workspace_id ON vulnerabilities(workspace_id);

-- Index para filtrar por scan_id
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_scan_id ON vulnerabilities(scan_id);

-- Index para filtrar por severidad
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_severity ON vulnerabilities(severity);

-- Index para filtrar por status
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_status ON vulnerabilities(status);

-- Index para ordenar por discovered_at
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_discovered_at ON vulnerabilities(discovered_at DESC);

-- Index compuesto workspace + severity (queries comunes)
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_workspace_severity ON vulnerabilities(workspace_id, severity);

-- Index compuesto workspace + status
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_workspace_status ON vulnerabilities(workspace_id, status);

-- Index para búsqueda por target
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_target ON vulnerabilities(target);

-- Index GIN para búsqueda full-text en description (PostgreSQL only)
-- CREATE INDEX IF NOT EXISTS idx_vulnerabilities_description_gin ON vulnerabilities USING gin(to_tsvector('english', description));

-- ============================================
-- REPORTS TABLE
-- ============================================

-- Index para filtrar por workspace
CREATE INDEX IF NOT EXISTS idx_reports_workspace_id ON reports(workspace_id);

-- Index para filtrar por tipo
CREATE INDEX IF NOT EXISTS idx_reports_report_type ON reports(report_type);

-- Index para filtrar por format
CREATE INDEX IF NOT EXISTS idx_reports_format ON reports(format);

-- Index para ordenar por created_at
CREATE INDEX IF NOT EXISTS idx_reports_created_at ON reports(created_at DESC);

-- Index compuesto workspace + tipo
CREATE INDEX IF NOT EXISTS idx_reports_workspace_type ON reports(workspace_id, report_type);

-- ============================================
-- AUDIT_LOGS TABLE
-- ============================================

-- Index para filtrar por user_id
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);

-- Index para filtrar por action
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);

-- Index para filtrar por resource_type
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_type ON audit_logs(resource_type);

-- Index para ordenar por timestamp (logs recientes)
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp DESC);

-- Index compuesto user + action (queries comunes)
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_action ON audit_logs(user_id, action);

-- Index para búsqueda por IP
CREATE INDEX IF NOT EXISTS idx_audit_logs_ip_address ON audit_logs(ip_address);

-- ============================================
-- VERIFICACIÓN
-- ============================================

-- Query para verificar índices creados
-- SELECT tablename, indexname, indexdef 
-- FROM pg_indexes 
-- WHERE schemaname = 'public' 
-- ORDER BY tablename, indexname;

-- ============================================
-- PERFORMANCE TIPS
-- ============================================

-- 1. Analizar tablas después de crear índices (PostgreSQL)
-- ANALYZE users;
-- ANALYZE workspaces;
-- ANALYZE scans;
-- ANALYZE scan_results;
-- ANALYZE vulnerabilities;
-- ANALYZE reports;
-- ANALYZE audit_logs;

-- 2. Vacuum para recuperar espacio (PostgreSQL)
-- VACUUM ANALYZE;

-- 3. Reindex si es necesario
-- REINDEX DATABASE pentesting_platform;

-- 4. Monitoring de uso de índices (PostgreSQL)
-- SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
-- FROM pg_stat_user_indexes
-- ORDER BY idx_scan DESC;

-- 5. Identificar índices no utilizados (PostgreSQL)
-- SELECT schemaname, tablename, indexname, idx_scan
-- FROM pg_stat_user_indexes
-- WHERE idx_scan = 0
-- AND indexrelname NOT LIKE 'pg_toast_%'
-- ORDER BY pg_relation_size(indexrelid) DESC;

