--
-- U-AIP Scoping Assistant - PostgreSQL Database Schema
-- Version: 1.0.0
-- Date: 2025-10-12
--
-- This schema supports the 5-stage interview process, session management,
-- and AI Project Charter generation for the U-AIP Scoping Assistant.
--

-- Enable UUID extension for primary keys
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- SESSIONS TABLE
-- ============================================================================
-- Stores user session state for multi-stage interview process

CREATE TABLE IF NOT EXISTS sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    project_name VARCHAR(500) NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    current_stage INTEGER NOT NULL DEFAULT 1 CHECK (current_stage >= 1 AND current_stage <= 6),
    status VARCHAR(50) NOT NULL DEFAULT 'in_progress'
        CHECK (status IN ('in_progress', 'completed', 'abandoned', 'paused')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for efficient session queries
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status) WHERE status = 'in_progress';
CREATE INDEX IF NOT EXISTS idx_sessions_updated ON sessions(last_updated_at DESC);

-- Trigger to automatically update last_updated_at
CREATE OR REPLACE FUNCTION update_sessions_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_sessions_updated
    BEFORE UPDATE ON sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_sessions_timestamp();

COMMENT ON TABLE sessions IS 'User sessions for U-AIP interview process';
COMMENT ON COLUMN sessions.session_id IS 'Unique session identifier (UUID)';
COMMENT ON COLUMN sessions.user_id IS 'Identifier for the user conducting the interview';
COMMENT ON COLUMN sessions.project_name IS 'Name of the AI project being scoped';
COMMENT ON COLUMN sessions.current_stage IS 'Current stage number (1-5), or 6 if completed';
COMMENT ON COLUMN sessions.status IS 'Session lifecycle status';

-- ============================================================================
-- STAGE DATA TABLE
-- ============================================================================
-- Stores structured responses for each stage deliverable

CREATE TABLE IF NOT EXISTS stage_data (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    stage_number INTEGER NOT NULL CHECK (stage_number >= 1 AND stage_number <= 5),
    field_name VARCHAR(255) NOT NULL,
    field_value JSONB NOT NULL,
    quality_score FLOAT CHECK (quality_score >= 0 AND quality_score <= 10),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, stage_number, field_name)
);

-- Indexes for stage data queries
CREATE INDEX IF NOT EXISTS idx_stage_data_session ON stage_data(session_id, stage_number);
CREATE INDEX IF NOT EXISTS idx_stage_data_field ON stage_data(field_name);
CREATE INDEX IF NOT EXISTS idx_stage_data_jsonb ON stage_data USING GIN (field_value);

-- Trigger to automatically update updated_at
CREATE OR REPLACE FUNCTION update_stage_data_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_stage_data_updated
    BEFORE UPDATE ON stage_data
    FOR EACH ROW
    EXECUTE FUNCTION update_stage_data_timestamp();

COMMENT ON TABLE stage_data IS 'Structured responses for each stage of the U-AIP protocol';
COMMENT ON COLUMN stage_data.stage_number IS 'Stage number (1=Business, 2=Value, 3=Data, 4=User, 5=Ethics)';
COMMENT ON COLUMN stage_data.field_name IS 'Name of the field within the stage deliverable';
COMMENT ON COLUMN stage_data.field_value IS 'JSONB value storing complex data structures';
COMMENT ON COLUMN stage_data.quality_score IS 'Response quality score from ResponseQualityAgent (0-10)';

-- ============================================================================
-- CONVERSATION HISTORY TABLE
-- ============================================================================
-- Stores complete Q&A conversation for audit trail and session replay

CREATE TABLE IF NOT EXISTS conversation_history (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    stage_number INTEGER CHECK (stage_number >= 1 AND stage_number <= 5),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Indexes for conversation retrieval
CREATE INDEX IF NOT EXISTS idx_conversation_session ON conversation_history(session_id, timestamp ASC);
CREATE INDEX IF NOT EXISTS idx_conversation_stage ON conversation_history(stage_number);
CREATE INDEX IF NOT EXISTS idx_conversation_metadata ON conversation_history USING GIN (metadata);

COMMENT ON TABLE conversation_history IS 'Complete conversation log for audit and replay';
COMMENT ON COLUMN conversation_history.role IS 'Message sender role (user, assistant, system)';
COMMENT ON COLUMN conversation_history.content IS 'Message content (question or response)';
COMMENT ON COLUMN conversation_history.metadata IS 'Additional context (agent_type, quality_score, etc.)';

-- ============================================================================
-- CHECKPOINTS TABLE
-- ============================================================================
-- Stores stage completion checkpoints for session recovery

CREATE TABLE IF NOT EXISTS checkpoints (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    stage_number INTEGER NOT NULL CHECK (stage_number >= 1 AND stage_number <= 5),
    checkpoint_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_snapshot JSONB NOT NULL,
    validation_passed BOOLEAN NOT NULL DEFAULT FALSE,
    validator_feedback JSONB DEFAULT NULL
);

-- Indexes for checkpoint queries
CREATE INDEX IF NOT EXISTS idx_checkpoints_session ON checkpoints(session_id, stage_number);
CREATE INDEX IF NOT EXISTS idx_checkpoints_timestamp ON checkpoints(checkpoint_timestamp DESC);

COMMENT ON TABLE checkpoints IS 'Stage completion checkpoints for session recovery';
COMMENT ON COLUMN checkpoints.data_snapshot IS 'Complete stage data at checkpoint time';
COMMENT ON COLUMN checkpoints.validation_passed IS 'Whether StageGateValidator approved progression';
COMMENT ON COLUMN checkpoints.validator_feedback IS 'Feedback from StageGateValidatorAgent';

-- ============================================================================
-- PROJECT CHARTERS TABLE
-- ============================================================================
-- Stores generated AI Project Charter documents

CREATE TABLE IF NOT EXISTS project_charters (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    charter_content JSONB NOT NULL,
    governance_decision VARCHAR(50) NOT NULL
        CHECK (governance_decision IN ('proceed', 'proceed_with_monitoring', 'revise', 'halt', 'submit_to_committee')),
    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    markdown_path VARCHAR(500),
    pdf_path VARCHAR(500),
    version VARCHAR(50) NOT NULL DEFAULT '1.0',
    UNIQUE(session_id)  -- One charter per session
);

-- Indexes for charter queries
CREATE INDEX IF NOT EXISTS idx_charters_session ON project_charters(session_id);
CREATE INDEX IF NOT EXISTS idx_charters_governance ON project_charters(governance_decision);
CREATE INDEX IF NOT EXISTS idx_charters_generated ON project_charters(generated_at DESC);

COMMENT ON TABLE project_charters IS 'Generated AI Project Charter documents';
COMMENT ON COLUMN project_charters.charter_content IS 'Complete charter as JSONB (AIProjectCharter dataclass)';
COMMENT ON COLUMN project_charters.governance_decision IS 'Ethical risk governance decision';
COMMENT ON COLUMN project_charters.markdown_path IS 'Filesystem path to markdown export';
COMMENT ON COLUMN project_charters.pdf_path IS 'Filesystem path to PDF export';

-- ============================================================================
-- QUALITY METRICS TABLE (Optional - for analytics)
-- ============================================================================
-- Tracks quality scores and reflection agent feedback

CREATE TABLE IF NOT EXISTS quality_metrics (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    stage_number INTEGER NOT NULL CHECK (stage_number >= 1 AND stage_number <= 5),
    question_id VARCHAR(255) NOT NULL,
    response_text TEXT NOT NULL,
    quality_score FLOAT NOT NULL CHECK (quality_score >= 0 AND quality_score <= 10),
    quality_issues JSONB DEFAULT '[]'::jsonb,
    followup_count INTEGER DEFAULT 0 CHECK (followup_count >= 0 AND followup_count <= 3),
    final_accepted BOOLEAN NOT NULL DEFAULT FALSE,
    evaluated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for analytics queries
CREATE INDEX IF NOT EXISTS idx_quality_metrics_session ON quality_metrics(session_id, stage_number);
CREATE INDEX IF NOT EXISTS idx_quality_metrics_score ON quality_metrics(quality_score);
CREATE INDEX IF NOT EXISTS idx_quality_metrics_followups ON quality_metrics(followup_count);

COMMENT ON TABLE quality_metrics IS 'Quality scores for analytics and continuous improvement';
COMMENT ON COLUMN quality_metrics.question_id IS 'Question identifier (e.g., S1Q1, S2Q3)';
COMMENT ON COLUMN quality_metrics.followup_count IS 'Number of quality loop iterations (max 3)';
COMMENT ON COLUMN quality_metrics.final_accepted IS 'Whether response was ultimately accepted';

-- ============================================================================
-- CONSISTENCY REPORTS TABLE
-- ============================================================================
-- Stores cross-stage consistency check results

CREATE TABLE IF NOT EXISTS consistency_reports (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    is_consistent BOOLEAN NOT NULL,
    overall_feasibility VARCHAR(50) NOT NULL
        CHECK (overall_feasibility IN ('high', 'medium', 'low', 'infeasible')),
    contradictions JSONB DEFAULT '[]'::jsonb,
    risk_areas JSONB DEFAULT '[]'::jsonb,
    recommendations JSONB DEFAULT '[]'::jsonb,
    checked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id)  -- One consistency report per session
);

-- Indexes for consistency report queries
CREATE INDEX IF NOT EXISTS idx_consistency_session ON consistency_reports(session_id);
CREATE INDEX IF NOT EXISTS idx_consistency_feasibility ON consistency_reports(overall_feasibility);

COMMENT ON TABLE consistency_reports IS 'Cross-stage consistency check results from ConsistencyCheckerAgent';
COMMENT ON COLUMN consistency_reports.contradictions IS 'Logical contradictions found across stages';
COMMENT ON COLUMN consistency_reports.risk_areas IS 'Feasibility risks identified';

-- ============================================================================
-- DATABASE FUNCTIONS
-- ============================================================================

-- Function to get active sessions count
CREATE OR REPLACE FUNCTION get_active_sessions_count()
RETURNS INTEGER AS $$
BEGIN
    RETURN (SELECT COUNT(*) FROM sessions WHERE status = 'in_progress');
END;
$$ LANGUAGE plpgsql;

-- Function to get session progress percentage
CREATE OR REPLACE FUNCTION get_session_progress(p_session_id UUID)
RETURNS INTEGER AS $$
DECLARE
    stage INT;
BEGIN
    SELECT current_stage INTO stage FROM sessions WHERE session_id = p_session_id;
    IF stage IS NULL THEN
        RETURN 0;
    END IF;
    RETURN ((stage - 1) * 20);  -- 0%, 20%, 40%, 60%, 80%, 100%
END;
$$ LANGUAGE plpgsql;

-- Function to mark session as abandoned if inactive for 24+ hours
CREATE OR REPLACE FUNCTION mark_abandoned_sessions()
RETURNS INTEGER AS $$
DECLARE
    updated_count INTEGER;
BEGIN
    UPDATE sessions
    SET status = 'abandoned'
    WHERE status = 'in_progress'
    AND last_updated_at < NOW() - INTERVAL '24 hours';

    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION mark_abandoned_sessions IS 'Mark sessions abandoned after 24 hours of inactivity';

-- ============================================================================
-- SAMPLE DATA (for development/testing only)
-- ============================================================================
-- Uncomment below to insert sample data for testing

/*
-- Sample session
INSERT INTO sessions (session_id, user_id, project_name, current_stage, status)
VALUES (
    '123e4567-e89b-12d3-a456-426614174000'::UUID,
    'test_user_1',
    'Customer Churn Prediction System',
    1,
    'in_progress'
);

-- Sample stage data
INSERT INTO stage_data (session_id, stage_number, field_name, field_value, quality_score)
VALUES (
    '123e4567-e89b-12d3-a456-426614174000'::UUID,
    1,
    'business_objective',
    '{"value": "Reduce customer churn by 25% within 12 months"}'::jsonb,
    8.5
);

-- Sample conversation
INSERT INTO conversation_history (session_id, role, content, stage_number)
VALUES (
    '123e4567-e89b-12d3-a456-426614174000'::UUID,
    'assistant',
    'Welcome to the U-AIP Scoping Assistant! What is your business objective?',
    1
);
*/

-- ============================================================================
-- PERMISSIONS (customize for your deployment)
-- ============================================================================

-- Example: Grant permissions to application user
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO uaip_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO uaip_app_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO uaip_app_user;

-- ============================================================================
-- COMPLETION
-- ============================================================================

-- Verify schema creation
DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name IN (
        'sessions',
        'stage_data',
        'conversation_history',
        'checkpoints',
        'project_charters',
        'quality_metrics',
        'consistency_reports'
    );

    RAISE NOTICE 'U-AIP Database Schema Initialized Successfully!';
    RAISE NOTICE 'Created % tables', table_count;
END $$;
