"""Added Correllation object

Revision ID: 3539bc0be183
Revises: 397062304318
Create Date: 2014-11-02 14:05:52.831088

"""

# revision identifiers, used by Alembic.
revision = '3539bc0be183'
down_revision = '397062304318'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('correlations')
    op.create_table('correllations',
    sa.Column('section_id', sa.Integer(), nullable=False),
    sa.Column('sensor_id', sa.Integer(), nullable=False),
    sa.Column('minimum', sa.Float(), nullable=True),
    sa.Column('low', sa.Float(), nullable=True),
    sa.Column('medium', sa.Float(), nullable=True),
    sa.Column('high', sa.Float(), nullable=True),
    sa.Column('huge', sa.Float(), nullable=True),
    sa.Column('trend_slope', sa.Float(), nullable=True),
    sa.Column('trend_samples', sa.Integer(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('backend_notes', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['section_id'], ['sections.id'], ),
    sa.ForeignKeyConstraint(['sensor_id'], ['sensors.id'], ),
    sa.PrimaryKeyConstraint('section_id', 'sensor_id')
    )
    #op.drop_table('spatial_ref_sys') 
    #op.drop_index('idx_gages_point', table_name='gages')
    #op.drop_index('idx_sections_path', table_name='sections')
    #op.drop_index('idx_sections_putin', table_name='sections')
    #op.drop_index('idx_sections_takeout', table_name='sections')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    #op.create_index('idx_sections_takeout', 'sections', ['takeout'], unique=False)
    #op.create_index('idx_sections_putin', 'sections', ['putin'], unique=False)
    #op.create_index('idx_sections_path', 'sections', ['path'], unique=False)
    #op.create_index('idx_gages_point', 'gages', ['point'], unique=False)
    op.drop_table('correllations')
    op.create_table('correlations',
    sa.Column('section', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('sensor', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('minimum', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('low', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('medium', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('high', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('huge', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('trend_slope', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('trend_samples', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('backend_notes', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('owner', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['owner'], [u'users.id'], name=u'correlations_owner_fkey'),
    sa.ForeignKeyConstraint(['section'], [u'sections.id'], name=u'correlations_section_fkey'),
    sa.ForeignKeyConstraint(['sensor'], [u'sensors.id'], name=u'correlations_sensor_fkey')
    )
    #op.create_table('spatial_ref_sys',
    #sa.Column('srid', sa.INTEGER(), autoincrement=False, nullable=False),
    #sa.Column('auth_name', sa.VARCHAR(length=256), autoincrement=False, nullable=True),
    #sa.Column('auth_srid', sa.INTEGER(), autoincrement=False, nullable=True),
    #sa.Column('srtext', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    #sa.Column('proj4text', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    #sa.PrimaryKeyConstraint('srid', name=u'spatial_ref_sys_pkey')
    #)
    
    ### end Alembic commands ###
