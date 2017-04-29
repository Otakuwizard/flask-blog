from flask import request, jsonify, g, current_app, url_for
from . import api
from ..models import Post, Comment, Permission
from .decorators import permission_required
from .errors import forbidden
from .. import db

@api.route('/posts/<id>')
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())
    
@api.route('/posts', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def new_post():
    post = post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, {'location': url_for('api.get_post', id=post.id, _external=True)}
    
@api.route('/posts/<id>', methods=['PUT'])
@permission_required(Permission.WRITE_ARTICLES)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.author or not g.current_user.is_administrator():
        return forbidden('insufficient permission')
    post.body = request.json.get('body', post.body)
    
@api.route('/posts')
def get_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.created_at.desc()).paginate(page, per_page=current_app.config.get('FLABY_API_POSTS_PER_PAGE', 10), error_out=False)
    posts = pagination.items
    prev = None if not pagination.has_prev else url_for('api.get_posts', page=page-1, _external=True)
    next = None if not pagination.has_next else url_for('api.get_posts', page=page+1, _external=True)
    
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })
    
@api.route('/posts/<id>/comments')
def get_post_comments(id):
    post = Post.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = post.comments.order_by(Comment.created_at.desc()).paginate(page, per_page=current_user.config.get('FLABY_API_POST_COMMENTS_PER_PAGE', 10), error_out=False)
    prev = None if not pagination.has_prev else url_for('api.get_post_comments', id=post.id, page=page-1, _external=True)
    next = None if not pagination.has_next else url_for('api.get_post_comments', id=post.id, page=page+1, _external=True)
    comments = pagination.items
    return jsonify({
        'comments': [comment.to_json() for comment in comments],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })