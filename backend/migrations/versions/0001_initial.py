"""Initial durable receipt, product and session schema."""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('users', sa.Column('id', sa.Integer, primary_key=True), sa.Column('name', sa.String(100), nullable=False), sa.Column('email', sa.String(254), nullable=False), sa.Column('password_hash', sa.String(255), nullable=False), sa.Column('currency', sa.String(3), nullable=False))
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_table('sessions', sa.Column('token_hash', sa.String(64), primary_key=True), sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False), sa.Column('expires', sa.DateTime(timezone=True), nullable=False))
    op.create_index('ix_sessions_user_id', 'sessions', ['user_id'])
    op.create_table('receipts', sa.Column('id', sa.Integer, primary_key=True), sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False), sa.Column('merchant', sa.String(200), nullable=False), sa.Column('purchase_date', sa.Date), sa.Column('category', sa.String(50), nullable=False), sa.Column('currency', sa.String(3), nullable=False), *[sa.Column(n, sa.Numeric(14, 2), nullable=n in ('subtotal', 'total')) for n in ['subtotal', 'tax', 'discount', 'fees', 'rounding', 'total']], sa.Column('status', sa.String(20), nullable=False), sa.Column('file_hash', sa.String(64), nullable=False), sa.Column('file_name', sa.String(100), nullable=False), sa.Column('original_name', sa.String(255), nullable=False), sa.Column('raw_text', sa.Text, nullable=False), sa.Column('ocr_lines', sa.JSON, nullable=False), sa.Column('warnings', sa.JSON, nullable=False), sa.Column('confidence', sa.Float, nullable=False), sa.Column('created_at', sa.DateTime(timezone=True), nullable=False))
    op.create_index('ix_receipts_user_id', 'receipts', ['user_id'])
    op.create_index('ix_receipts_file_hash', 'receipts', ['file_hash'])
    op.create_table('items', sa.Column('id', sa.Integer, primary_key=True), sa.Column('receipt_id', sa.Integer, sa.ForeignKey('receipts.id'), nullable=False), sa.Column('name', sa.String(200), nullable=False), sa.Column('quantity', sa.Numeric(12, 3), nullable=False), sa.Column('unit', sa.String(10), nullable=False), sa.Column('amount', sa.Numeric(14, 2), nullable=False), sa.Column('line_index', sa.Integer), sa.Column('product_key', sa.String(200)))
    op.create_index('ix_items_receipt_id', 'items', ['receipt_id'])
    op.create_table('decisions', sa.Column('id', sa.Integer, primary_key=True), sa.Column('receipt_id', sa.Integer, sa.ForeignKey('receipts.id'), nullable=False), sa.Column('alert_key', sa.String(200), nullable=False), sa.Column('action', sa.String(20), nullable=False), sa.UniqueConstraint('receipt_id', 'alert_key'))

def downgrade():
    for table in ['decisions', 'items', 'receipts', 'sessions', 'users']:
        op.drop_table(table)
