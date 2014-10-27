"""added name, slug, prefix, suffix to Sensor

Revision ID: 1b1cf96dafa2
Revises: 49d0b696f95e
Create Date: 2014-10-26 22:52:34.733936

"""

# revision identifiers, used by Alembic.
revision = '1b1cf96dafa2'
down_revision = '49d0b696f95e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    #op.drop_table('spatial_ref_sys')
    #op.drop_index('idx_gages_point', table_name='gages')
    #op.drop_index('idx_sections_path', table_name='sections')
    #op.drop_index('idx_sections_putin', table_name='sections')
    #op.drop_index('idx_sections_takeout', table_name='sections')
    op.add_column('sensors', sa.Column('name', sa.String(length=80), nullable=True))
    op.add_column('sensors', sa.Column('prefix', sa.String(length=10), nullable=True))
    op.add_column('sensors', sa.Column('slug', sa.String(length=40), nullable=True))
    op.add_column('sensors', sa.Column('suffix', sa.String(length=10), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sensors', 'suffix')
    op.drop_column('sensors', 'slug')
    op.drop_column('sensors', 'prefix')
    op.drop_column('sensors', 'name')
    #op.create_index('idx_sections_takeout', 'sections', ['takeout'], unique=False)
    #op.create_index('idx_sections_putin', 'sections', ['putin'], unique=False)
    #op.create_index('idx_sections_path', 'sections', ['path'], unique=False)
    #op.create_index('idx_gages_point', 'gages', ['point'], unique=False)
    #op.create_table('spatial_ref_sys',
    #sa.Column('srid', sa.INTEGER(), autoincrement=False, nullable=False),
    #sa.Column('auth_name', sa.VARCHAR(length=256), autoincrement=False, nullable=True),
    #sa.Column('auth_srid', sa.INTEGER(), autoincrement=False, nullable=True),
    #sa.Column('srtext', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    #sa.Column('proj4text', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    #sa.PrimaryKeyConstraint('srid', name=u'spatial_ref_sys_pkey')
    #)
    ### end Alembic commands ###
