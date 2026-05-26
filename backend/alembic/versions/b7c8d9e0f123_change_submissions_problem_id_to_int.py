"""change submissions problem_id to integer foreign key

Revision ID: b7c8d9e0f123
Revises: a1b2c3d4e5f6
Create Date: 2026-05-11 16:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7c8d9e0f123'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE submissions DROP CONSTRAINT IF EXISTS submissions_problem_id_fkey")
    op.alter_column(
        'submissions',
        'problem_id',
        existing_type=sa.String(length=100),
        type_=sa.Integer(),
        postgresql_using="NULLIF(problem_id, '')::integer",
        existing_nullable=True,
    )
    op.create_foreign_key(
        'submissions_problem_id_fkey',
        'submissions',
        'problems',
        ['problem_id'],
        ['id'],
    )
    op.create_index(op.f('ix_submissions_problem_id'), 'submissions', ['problem_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_submissions_problem_id'), table_name='submissions')
    op.execute("ALTER TABLE submissions DROP CONSTRAINT IF EXISTS submissions_problem_id_fkey")
    op.alter_column(
        'submissions',
        'problem_id',
        existing_type=sa.Integer(),
        type_=sa.String(length=100),
        postgresql_using='problem_id::text',
        existing_nullable=True,
    )
