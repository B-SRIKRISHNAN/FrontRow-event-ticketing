"""Initial database schema creation

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-25 18:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', name='uq_users_email')
    )

    # 2. Create events table
    op.create_table(
        'events',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('venue_name', sa.String(length=255), nullable=False),
        sa.Column('show_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. Create orders table
    op.create_table(
        'orders',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 4. Create holds table (UUID primary key)
    op.create_table(
        'holds',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_id', sa.BigInteger(), sa.ForeignKey('events.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='ACTIVE', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('order_id', sa.BigInteger(), sa.ForeignKey('orders.id', ondelete='SET NULL'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_holds_expires_at', 'holds', ['expires_at'])
    op.create_index('idx_holds_order_id', 'holds', ['order_id'])

    # 5. Create seats table
    op.create_table(
        'seats',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('event_id', sa.BigInteger(), sa.ForeignKey('events.id', ondelete='CASCADE'), nullable=False),
        sa.Column('row', sa.String(length=10), nullable=False),
        sa.Column('seat_number', sa.Integer(), nullable=False),
        sa.Column('section', sa.String(length=50), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('status', sa.String(length=20), server_default='AVAILABLE', nullable=False),
        sa.Column('current_hold_id', sa.UUID(), sa.ForeignKey('holds.id', ondelete='SET NULL'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id', 'row', 'seat_number', name='uq_seats_event_row_number')
    )
    op.create_index('idx_seats_current_hold_id', 'seats', ['current_hold_id'])
    op.create_index('idx_seats_event_id', 'seats', ['event_id'])

    # 6. Create tickets table
    op.create_table(
        'tickets',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('order_id', sa.BigInteger(), sa.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('seat_id', sa.BigInteger(), sa.ForeignKey('seats.id', ondelete='CASCADE'), nullable=False),
        sa.Column('price_paid', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('tickets')
    op.drop_index('idx_seats_event_id', table_name='seats')
    op.drop_index('idx_seats_current_hold_id', table_name='seats')
    op.drop_table('seats')
    op.drop_index('idx_holds_order_id', table_name='holds')
    op.drop_index('idx_holds_expires_at', table_name='holds')
    op.drop_table('holds')
    op.drop_table('orders')
    op.drop_table('events')
    op.drop_table('users')
