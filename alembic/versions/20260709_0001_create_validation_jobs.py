"""create validation_jobs table

Revision ID: 20260709_0001
Revises:
Create Date: 2026-07-09
"""
from alembic import op
import sqlalchemy as sa


revision = '20260709_0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'validation_jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('celery_task_id', sa.String(length=255), nullable=False),
        sa.Column('input_type', sa.String(length=32), nullable=False),
        sa.Column('input_value', sa.String(length=512), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('result', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_validation_jobs_celery_task_id'),
        'validation_jobs',
        ['celery_task_id'],
        unique=False,
    )


def downgrade():
    op.drop_index(op.f('ix_validation_jobs_celery_task_id'), table_name='validation_jobs')
    op.drop_table('validation_jobs')
