"""empty message

Revision ID: 2a2873f5a2dd
Revises: None
Create Date: 2014-10-21 20:19:36.656824

"""

# revision identifiers, used by Alembic.
revision = '2a2873f5a2dd'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('spatial_ref_sys')
    op.drop_index('idx_gages_point', table_name='gages')
    op.add_column('samples', sa.Column('level', sa.Float(), nullable=True))
    op.drop_index('idx_sections_path', table_name='sections')
    op.drop_index('idx_sections_putin', table_name='sections')
    op.drop_index('idx_sections_takeout', table_name='sections')
    op.add_column('users', sa.Column('password_hash', sa.String(length=128), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'password_hash')
    op.create_index('idx_sections_takeout', 'sections', ['takeout'], unique=False)
    op.create_index('idx_sections_putin', 'sections', ['putin'], unique=False)
    op.create_index('idx_sections_path', 'sections', ['path'], unique=False)
    op.drop_column('samples', 'level')
    op.create_index('idx_gages_point', 'gages', ['point'], unique=False)
    op.create_table('spatial_ref_sys',
    sa.Column('srid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('auth_name', sa.VARCHAR(length=256), autoincrement=False, nullable=True),
    sa.Column('auth_srid', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('srtext', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    sa.Column('proj4text', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('srid', name=u'spatial_ref_sys_pkey')
    )
    ### end Alembic commands ###
