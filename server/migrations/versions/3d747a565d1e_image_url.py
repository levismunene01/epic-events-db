"""image_url

Revision ID: 3d747a565d1e
Revises: ec4e870ce20c
Create Date: 2024-08-07 17:40:57.388654

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3d747a565d1e'
down_revision = 'ec4e870ce20c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.alter_column('image',
               existing_type=postgresql.BYTEA(),
               type_=sa.String(),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('events', schema=None) as batch_op:
        batch_op.alter_column('image',
               existing_type=sa.String(),
               type_=postgresql.BYTEA(),
               existing_nullable=False)

    # ### end Alembic commands ###
