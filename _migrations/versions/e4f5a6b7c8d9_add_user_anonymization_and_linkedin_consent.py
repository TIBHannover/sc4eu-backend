"""add user anonymization timestamps and linkedin publication consent

Revision ID: e4f5a6b7c8d9
Revises: b1a2c3d4e5f6
Create Date: 2026-11-12 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e4f5a6b7c8d9'
down_revision = 'b1a2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('sc3_user_model', schema=None) as batch_op:
        batch_op.add_column(sa.Column('anonymized_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('deletion_requested_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
        # opt-in: existing users are opted out until they agree
        batch_op.add_column(sa.Column('linkedin_publication_consent', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade():
    with op.batch_alter_table('sc3_user_model', schema=None) as batch_op:
        batch_op.drop_column('linkedin_publication_consent')
        batch_op.drop_column('deleted_at')
        batch_op.drop_column('deletion_requested_at')
        batch_op.drop_column('anonymized_at')
