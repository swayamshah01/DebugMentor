"""phase_1_add_patterns_problems_testcases

Revision ID: a1b2c3d4e5f6
Revises: 2fd46b23f9c4
Create Date: 2026-05-11 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '2fd46b23f9c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create patterns table
    op.create_table('patterns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon_name', sa.String(length=50), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_patterns_id'), 'patterns', ['id'], unique=False)
    op.create_index(op.f('ix_patterns_name'), 'patterns', ['name'], unique=True)
    op.create_index(op.f('ix_patterns_slug'), 'patterns', ['slug'], unique=True)

    # Create problems table
    op.create_table('problems',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pattern_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('slug', sa.String(length=200), nullable=False),
        sa.Column('difficulty', sa.String(length=20), nullable=False),
        sa.Column('short_description', sa.Text(), nullable=True),
        sa.Column('statement', sa.Text(), nullable=False),
        sa.Column('constraints_text', sa.Text(), nullable=True),
        sa.Column('examples_json', sa.JSON(), nullable=True),
        sa.Column('starter_code_json', sa.JSON(), nullable=True),
        sa.Column('reference_solution_json', sa.JSON(), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['pattern_id'], ['patterns.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_problems_id'), 'problems', ['id'], unique=False)
    op.create_index(op.f('ix_problems_pattern_id'), 'problems', ['pattern_id'], unique=False)
    op.create_index(op.f('ix_problems_slug'), 'problems', ['slug'], unique=True)

    # Create test_cases table
    op.create_table('test_cases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('problem_id', sa.Integer(), nullable=False),
        sa.Column('label', sa.String(length=200), nullable=False),
        sa.Column('input', sa.Text(), nullable=False),
        sa.Column('expected_output', sa.Text(), nullable=False),
        sa.Column('is_hidden', sa.Boolean(), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['problem_id'], ['problems.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_test_cases_id'), 'test_cases', ['id'], unique=False)
    op.create_index(op.f('ix_test_cases_problem_id'), 'test_cases', ['problem_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_test_cases_problem_id'), table_name='test_cases')
    op.drop_index(op.f('ix_test_cases_id'), table_name='test_cases')
    op.drop_table('test_cases')

    op.drop_index(op.f('ix_problems_slug'), table_name='problems')
    op.drop_index(op.f('ix_problems_pattern_id'), table_name='problems')
    op.drop_index(op.f('ix_problems_id'), table_name='problems')
    op.drop_table('problems')

    op.drop_index(op.f('ix_patterns_slug'), table_name='patterns')
    op.drop_index(op.f('ix_patterns_name'), table_name='patterns')
    op.drop_index(op.f('ix_patterns_id'), table_name='patterns')
    op.drop_table('patterns')
