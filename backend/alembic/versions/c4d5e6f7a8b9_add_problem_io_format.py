"""add problem input and output format

Revision ID: c4d5e6f7a8b9
Revises: b7c8d9e0f123
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c4d5e6f7a8b9"
down_revision: Union[str, None] = "b7c8d9e0f123"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("problems", sa.Column("input_format", sa.Text(), nullable=True))
    op.add_column("problems", sa.Column("output_format", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("problems", "output_format")
    op.drop_column("problems", "input_format")
