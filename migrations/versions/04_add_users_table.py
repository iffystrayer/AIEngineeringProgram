"""Add users table for authentication

Revision ID: 04_add_users_table
Revises: 03033cebb647
Create Date: 2025-10-24 20:30:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "04_add_users_table"
down_revision = "03033cebb647"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create users table for authentication."""
    op.create_table(
        "users",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("user_id"),
    )

    # Create indexes
    op.create_index("idx_users_email", "users", ["email"], unique=True)
    op.create_index("idx_users_created_at", "users", [sa.text("created_at DESC")])

    # Add user_id foreign key to sessions table if not exists
    try:
        op.add_column(
            "sessions",
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        )
        op.create_foreign_key(
            "fk_sessions_user_id",
            "sessions",
            "users",
            ["user_id"],
            ["user_id"],
            ondelete="CASCADE",
        )
    except Exception:
        # Column may already exist
        pass


def downgrade() -> None:
    """Drop users table and related constraints."""
    # Drop foreign key first
    try:
        op.drop_constraint("fk_sessions_user_id", "sessions", type_="foreignkey")
    except Exception:
        pass

    # Drop user_id column from sessions if it exists
    try:
        op.drop_column("sessions", "user_id")
    except Exception:
        pass

    # Drop indexes
    op.drop_index("idx_users_created_at", table_name="users")
    op.drop_index("idx_users_email", table_name="users")

    # Drop table
    op.drop_table("users")
