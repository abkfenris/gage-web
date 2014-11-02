"""Addded remote_parameter to Sensor

Revision ID: 397062304318
Revises: 2a1a8c93982
Create Date: 2014-11-02 11:44:46.658818

"""

# revision identifiers, used by Alembic.
revision = '397062304318'
down_revision = '2a1a8c93982'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    #op.drop_table('spatial_ref_sys')
    #op.drop_index('idx_gages_point', table_name='gages')
    #op.drop_index('idx_sections_path', table_name='sections')
    #op.drop_index('idx_sections_putin', table_name='sections')
    #op.drop_index('idx_sections_takeout', table_name='sections')
    op.add_column('sensors', sa.Column('remote_parameter', sa.String(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sensors', 'remote_parameter')
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
