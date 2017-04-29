from flask import g, current_app, url_for, request, jsonify
from . import api
from .errors import forbidden
from .decorators import permission_required
from ..models import Comment, Post, Permission
from .. import db

@api.route('/comments/<id>')
def get_comment(id):
    comment = Comment,query.get_or_404(id)
    return jsonify(comment.to_json())
    
@api.route('/posts/<id>/comments', methods=['POST'])
@permission_required(Permission.COMMENTS)
def new_comment(id):
    post = Post.query.get_or_404(id)
    comment = Comment.from_json(request.json)
    comment.author = g.current_user
    comment.post = post
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_json()), 201, {'location': url_for('api.get_comment', id=comment.id, _external=True)}
    
@api.route('/comments')
@permission_required(Permission.MODERATE_COMMENTS)
def get_comments():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.created_at.desc()).paginate(page, per_page=current_app.config.get('FLABY_COMMENTS_PER_PAGE', 10), error_out=False)
    comments = pagination.items
    prev = None if not pagination.has_prev else url_for('api.get_comments', page=page-1, _external=True)
    next = None if not pagination.has_next else url_for('api.get_comments', page=page+1, _external=True)
    return jsonify({
        'comments': [comment.to_json() for comment in comments],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })