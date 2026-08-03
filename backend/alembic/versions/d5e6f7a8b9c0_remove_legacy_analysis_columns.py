"""remove unused legacy analysis columns

Revision ID: d5e6f7a8b9c0
Revises: c4d5e6f7a8b9
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d5e6f7a8b9c0"
down_revision: Union[str, None] = "c4d5e6f7a8b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("submissions", "ast_findings")
    op.drop_column("submissions", "feedback")
    op.drop_column("problems", "reference_solution_json")
    op.drop_column("users", "error_pattern")
    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.String(length=255),
        server_default=None,
        existing_nullable=False,
    )


def downgrade() -> None:
    op.add_column("users", sa.Column("error_pattern", sa.Text(), nullable=True))
    op.add_column(
        "problems",
        sa.Column("reference_solution_json", sa.JSON(), nullable=True),
    )
    op.add_column("submissions", sa.Column("feedback", sa.Text(), nullable=True))
    op.add_column("submissions", sa.Column("ast_findings", sa.JSON(), nullable=True))
