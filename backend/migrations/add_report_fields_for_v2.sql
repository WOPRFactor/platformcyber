-- Migration: Add extended fields to Report model for Reporting V2
-- Date: 2025-12-10
-- Description: Adds versionado, metadata de contenido, y metadata de procesamiento
-- to the reports table to support the new reporting V2 module

-- Add versionado fields
ALTER TABLE reports ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1 NOT NULL;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS is_latest BOOLEAN DEFAULT TRUE NOT NULL;

-- Add file security field
ALTER TABLE reports ADD COLUMN IF NOT EXISTS file_hash VARCHAR(64);

-- Add metadata del contenido fields
ALTER TABLE reports ADD COLUMN IF NOT EXISTS total_findings INTEGER DEFAULT 0;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS critical_count INTEGER DEFAULT 0;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS high_count INTEGER DEFAULT 0;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS medium_count INTEGER DEFAULT 0;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS low_count INTEGER DEFAULT 0;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS info_count INTEGER DEFAULT 0;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS risk_score FLOAT;

-- Add metadata de procesamiento fields
ALTER TABLE reports ADD COLUMN IF NOT EXISTS files_processed INTEGER DEFAULT 0;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS tools_used JSON;
ALTER TABLE reports ADD COLUMN IF NOT EXISTS generation_time_seconds FLOAT;

-- Add error tracking field
ALTER TABLE reports ADD COLUMN IF NOT EXISTS error_message TEXT;

-- Update status default for existing rows (optional, only if needed)
-- ALTER TABLE reports ALTER COLUMN status SET DEFAULT 'pending';

-- Create indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_reports_workspace_type ON reports(workspace_id, report_type);
CREATE INDEX IF NOT EXISTS idx_reports_created_at ON reports(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status);
CREATE INDEX IF NOT EXISTS idx_reports_is_latest ON reports(is_latest) WHERE is_latest = TRUE;

-- Comments for documentation
COMMENT ON COLUMN reports.version IS 'Version number for report versioning';
COMMENT ON COLUMN reports.is_latest IS 'Flag to mark the latest version of a report';
COMMENT ON COLUMN reports.file_hash IS 'SHA-256 hash of the report file for integrity verification';
COMMENT ON COLUMN reports.total_findings IS 'Total number of findings in the report';
COMMENT ON COLUMN reports.risk_score IS 'Overall risk score (0-10) calculated from findings';
COMMENT ON COLUMN reports.files_processed IS 'Number of files processed during report generation';
COMMENT ON COLUMN reports.tools_used IS 'JSON array of tool names used in the scan';
COMMENT ON COLUMN reports.generation_time_seconds IS 'Time taken to generate the report in seconds';
COMMENT ON COLUMN reports.error_message IS 'Error message if report generation failed';



