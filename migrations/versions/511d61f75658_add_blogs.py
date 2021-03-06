"""add blogs

Revision ID: 511d61f75658
Revises: 4221dc540ee2
Create Date: 2017-05-11 11:32:29.195147

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '511d61f75658'
down_revision = '4221dc540ee2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blogs',
    sa.Column('id', sa.String(length=64), nullable=False),
    sa.Column('title', sa.String(length=32), nullable=False),
    sa.Column('summary', sa.String(length=256), nullable=False),
    sa.Column('body', sa.Text(), nullable=True),
    sa.Column('body_html', sa.Text(), nullable=True),
    sa.Column('author_id', sa.String(length=64), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('last_edit', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('comments', sa.Column('blog_id', sa.String(length=64), nullable=True))
    op.create_foreign_key(None, 'comments', 'blogs', ['blog_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'comments', type_='foreignkey')
    op.drop_column('comments', 'blog_id')
    op.drop_table('blogs')
    # ### end Alembic commands ###
