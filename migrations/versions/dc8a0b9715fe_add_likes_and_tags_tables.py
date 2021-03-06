"""add likes and tags tables

Revision ID: dc8a0b9715fe
Revises: 511d61f75658
Create Date: 2017-05-22 19:39:43.026241

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dc8a0b9715fe'
down_revision = '511d61f75658'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tags',
    sa.Column('id', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('blog_tags',
    sa.Column('blog_id', sa.String(length=64), nullable=True),
    sa.Column('tag_id', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['blog_id'], ['blogs.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], )
    )
    op.create_table('userlikes',
    sa.Column('id', sa.String(length=64), nullable=False),
    sa.Column('user_id', sa.String(length=64), nullable=True),
    sa.Column('liked_post_id', sa.String(length=64), nullable=True),
    sa.Column('disliked_post_id', sa.String(length=64), nullable=True),
    sa.Column('liked_blog_id', sa.String(length=64), nullable=True),
    sa.Column('disliked_blog_id', sa.String(length=64), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['disliked_blog_id'], ['blogs.id'], ),
    sa.ForeignKeyConstraint(['disliked_post_id'], ['posts.id'], ),
    sa.ForeignKeyConstraint(['liked_blog_id'], ['blogs.id'], ),
    sa.ForeignKeyConstraint(['liked_post_id'], ['posts.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('userlikes')
    op.drop_table('blog_tags')
    op.drop_table('tags')
    # ### end Alembic commands ###
