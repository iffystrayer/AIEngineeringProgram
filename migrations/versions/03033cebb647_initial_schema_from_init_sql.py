"""Initial schema from init.sql

Revision ID: 03033cebb647
Revises: 
Create Date: 2025-10-24 18:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '03033cebb647'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create complete U-AIP database schema from init.sql"""
    
    # Enable UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Create sessions table
    op.create_table(
        'sessions',
        sa.Column('session_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('project_name', sa.String(500), nullable=False),
        sa.Column('started_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('current_stage', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('status', sa.String(50), nullable=False, server_default='in_progress'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint('current_stage >= 1 AND current_stage <= 6', name='sessions_current_stage_check'),
        sa.CheckConstraint("status IN ('in_progress', 'completed', 'abandoned', 'paused')", name='sessions_status_check')
    )
    
    op.create_index('idx_sessions_user_id', 'sessions', ['user_id', sa.text('started_at DESC')])
    op.create_index('idx_sessions_status', 'sessions', ['status'], postgresql_where=sa.text("status = 'in_progress'"))
    op.create_index('idx_sessions_updated', 'sessions', [sa.text('last_updated_at DESC')])
    
    op.execute("""
        CREATE OR REPLACE FUNCTION update_sessions_timestamp()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.last_updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
    """)
    
    op.execute("""
        CREATE TRIGGER trigger_sessions_updated
            BEFORE UPDATE ON sessions
            FOR EACH ROW
            EXECUTE FUNCTION update_sessions_timestamp()
    """)
    
    # Create stage_data table
    op.create_table(
        'stage_data',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('stage_number', sa.Integer(), nullable=False),
        sa.Column('field_name', sa.String(255), nullable=False),
        sa.Column('field_value', postgresql.JSONB(), nullable=False),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.session_id'], ondelete='CASCADE'),
        sa.CheckConstraint('stage_number >= 1 AND stage_number <= 5', name='stage_data_stage_number_check'),
        sa.CheckConstraint('quality_score >= 0 AND quality_score <= 10', name='stage_data_quality_score_check'),
        sa.UniqueConstraint('session_id', 'stage_number', 'field_name', name='stage_data_session_stage_field_key')
    )
    
    op.create_index('idx_stage_data_session', 'stage_data', ['session_id', 'stage_number'])
    op.create_index('idx_stage_data_field', 'stage_data', ['field_name'])
    op.create_index('idx_stage_data_jsonb', 'stage_data', ['field_value'], postgresql_using='gin')
    
    op.execute("""
        CREATE OR REPLACE FUNCTION update_stage_data_timestamp()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
    """)
    
    op.execute("""
        CREATE TRIGGER trigger_stage_data_updated
            BEFORE UPDATE ON stage_data
            FOR EACH ROW
            EXECUTE FUNCTION update_stage_data_timestamp()
    """)
    
    # Create conversation_history table
    op.create_table(
        'conversation_history',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('stage_number', sa.Integer(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True, server_default=sa.text("'{}'::jsonb")),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.session_id'], ondelete='CASCADE'),
        sa.CheckConstraint("role IN ('user', 'assistant', 'system')", name='conversation_history_role_check'),
        sa.CheckConstraint('stage_number >= 1 AND stage_number <= 5', name='conversation_history_stage_number_check')
    )
    
    op.create_index('idx_conversation_session', 'conversation_history', ['session_id', sa.text('timestamp ASC')])
    op.create_index('idx_conversation_stage', 'conversation_history', ['stage_number'])
    op.create_index('idx_conversation_metadata', 'conversation_history', ['metadata'], postgresql_using='gin')
    
    # Create checkpoints table
    op.create_table(
        'checkpoints',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('stage_number', sa.Integer(), nullable=False),
        sa.Column('checkpoint_timestamp', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('data_snapshot', postgresql.JSONB(), nullable=False),
        sa.Column('validation_passed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('validator_feedback', postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.session_id'], ondelete='CASCADE'),
        sa.CheckConstraint('stage_number >= 1 AND stage_number <= 5', name='checkpoints_stage_number_check')
    )
    
    op.create_index('idx_checkpoints_session', 'checkpoints', ['session_id', 'stage_number'])
    op.create_index('idx_checkpoints_timestamp', 'checkpoints', [sa.text('checkpoint_timestamp DESC')])
    
    # Create project_charters table
    op.create_table(
        'project_charters',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('charter_content', postgresql.JSONB(), nullable=False),
        sa.Column('governance_decision', sa.String(50), nullable=False),
        sa.Column('generated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('markdown_path', sa.String(500), nullable=True),
        sa.Column('pdf_path', sa.String(500), nullable=True),
        sa.Column('version', sa.String(50), nullable=False, server_default="'1.0'"),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.session_id'], ondelete='CASCADE'),
        sa.CheckConstraint("governance_decision IN ('proceed', 'proceed_with_monitoring', 'revise', 'halt', 'submit_to_committee')", name='project_charters_governance_decision_check'),
        sa.UniqueConstraint('session_id', name='project_charters_session_id_key')
    )
    
    op.create_index('idx_charters_session', 'project_charters', ['session_id'])
    op.create_index('idx_charters_governance', 'project_charters', ['governance_decision'])
    op.create_index('idx_charters_generated', 'project_charters', [sa.text('generated_at DESC')])
    
    # Create quality_metrics table
    op.create_table(
        'quality_metrics',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('stage_number', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.String(255), nullable=False),
        sa.Column('response_text', sa.Text(), nullable=False),
        sa.Column('quality_score', sa.Float(), nullable=False),
        sa.Column('quality_issues', postgresql.JSONB(), nullable=True, server_default=sa.text("'[]'::jsonb")),
        sa.Column('followup_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('final_accepted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('evaluated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.session_id'], ondelete='CASCADE'),
        sa.CheckConstraint('stage_number >= 1 AND stage_number <= 5', name='quality_metrics_stage_number_check'),
        sa.CheckConstraint('quality_score >= 0 AND quality_score <= 10', name='quality_metrics_quality_score_check'),
        sa.CheckConstraint('followup_count >= 0 AND followup_count <= 3', name='quality_metrics_followup_count_check')
    )
    
    op.create_index('idx_quality_metrics_session', 'quality_metrics', ['session_id', 'stage_number'])
    op.create_index('idx_quality_metrics_score', 'quality_metrics', ['quality_score'])
    op.create_index('idx_quality_metrics_followups', 'quality_metrics', ['followup_count'])
    
    # Create consistency_reports table
    op.create_table(
        'consistency_reports',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_consistent', sa.Boolean(), nullable=False),
        sa.Column('overall_feasibility', sa.String(50), nullable=False),
        sa.Column('contradictions', postgresql.JSONB(), nullable=True, server_default=sa.text("'[]'::jsonb")),
        sa.Column('risk_areas', postgresql.JSONB(), nullable=True, server_default=sa.text("'[]'::jsonb")),
        sa.Column('recommendations', postgresql.JSONB(), nullable=True, server_default=sa.text("'[]'::jsonb")),
        sa.Column('checked_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.session_id'], ondelete='CASCADE'),
        sa.CheckConstraint("overall_feasibility IN ('high', 'medium', 'low', 'infeasible')", name='consistency_reports_overall_feasibility_check'),
        sa.UniqueConstraint('session_id', name='consistency_reports_session_id_key')
    )
    
    op.create_index('idx_consistency_session', 'consistency_reports', ['session_id'])
    op.create_index('idx_consistency_feasibility', 'consistency_reports', ['overall_feasibility'])
    
    # Create helper functions
    op.execute("""
        CREATE OR REPLACE FUNCTION get_active_sessions_count()
        RETURNS INTEGER AS $$
        BEGIN
            RETURN (SELECT COUNT(*) FROM sessions WHERE status = 'in_progress');
        END;
        $$ LANGUAGE plpgsql
    """)
    
    op.execute("""
        CREATE OR REPLACE FUNCTION get_session_progress(p_session_id UUID)
        RETURNS INTEGER AS $$
        DECLARE
            stage INT;
        BEGIN
            SELECT current_stage INTO stage FROM sessions WHERE session_id = p_session_id;
            IF stage IS NULL THEN
                RETURN 0;
            END IF;
            RETURN ((stage - 1) * 20);
        END;
        $$ LANGUAGE plpgsql
    """)
    
    op.execute("""
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
        $$ LANGUAGE plpgsql
    """)


def downgrade() -> None:
    """Drop all tables and functions"""
    
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table('consistency_reports')
    op.drop_table('quality_metrics')
    op.drop_table('project_charters')
    op.drop_table('checkpoints')
    op.drop_table('conversation_history')
    op.drop_table('stage_data')
    op.drop_table('sessions')
    
    # Drop functions
    op.execute('DROP FUNCTION IF EXISTS mark_abandoned_sessions()')
    op.execute('DROP FUNCTION IF EXISTS get_session_progress(UUID)')
    op.execute('DROP FUNCTION IF EXISTS get_active_sessions_count()')
    op.execute('DROP FUNCTION IF EXISTS update_stage_data_timestamp()')
    op.execute('DROP FUNCTION IF EXISTS update_sessions_timestamp()')
    
    # Drop extension
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
