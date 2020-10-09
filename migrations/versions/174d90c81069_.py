"""empty message

Revision ID: 174d90c81069
Revises: ae4ad207787a
Create Date: 2020-10-08 19:11:51.224922

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '174d90c81069'
down_revision = 'ae4ad207787a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('website', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'website')
    # ### end Alembic commands ###