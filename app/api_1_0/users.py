from flask import request, url_for, jsonify, g, current_app
from . import api
from ..models import User, Post, Comment, Follow
from .. import db
from .exceptions import ValidationError

@api.route('/users/<id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())
    
@api.route('/users', methods=['POST'])
def new_user():
    user = User.from_json(request.json)
    db.session.add(user)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise ValidationError('Invalid Register Information')
    return jsonify(user.to_json()), 201, {'location': url_for('api.get_user', id=user.id, _external=True)}
    
@api.route('/users/<id>/posts')
def get_user_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.created_at.desc()).paginate(page, per_page=current_app.config.get('FLABY_USER_POSTS_PER_PAGE', 10), error_out=False)
    posts = pagination.items
    prev = None if not pagination.has_prev else url_for('api.get_user_posts', page=page-1, _external=True)
    next = None if not pagination.has_next else url_for('api.get_user_posts', page=page+1, _external=True)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })
    
@api.route('/users/<id>/followed')
def get_user_followed(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.folllowed.order_by(Follow.created_at.desc()).paginate(page, per_page=current_app.config.get('FLABY_USER_FOLLOWED_PER_PAGE', 10), error_out=False)
    followed = [follow.followed for follow in pagination.items]
    prev = None if not pagination.has_prev else url_for('api.get_user_followed', page=page-1, _external=True)
    next = None if not pagination.has_next else url_for('api.get_user_followed', page=page+1, _external=True)
    return jsonify({
        'followed': [user.to_json() for user in followed],
        'prev': prev,
        'next': next,
        'count': pagination.total-1
    })
    
@api.route('/users/<id>/followers')
def get_user_followers(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.folllowers.order_by(Follow.created_at.desc()).paginate(page, per_page=current_app.config.get('FLABY_USER_FOLLOWERS_PER_PAGE', 10), error_out=False)
    followers = [follow.follower for follow in pagination.items]
    prev = None if not pagination.has_prev else url_for('api.get_user_followers', page=page-1, _external=True)
    next = None if not pagination.has_next else url_for('api.get_user_followers', page=page+1, _external=True)
    return jsonify({
        'followers': [user.to_json() for user in followers],
        'prev': prev,
        'next': next,
        'count': pagination.total-1
    })
    
@api.route('/users/<id>/followed-posts')
def get_user_followed_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.followed_posts.order_by(Post.created_at.desc()).paginate(page, per_page=current_app.config.get('FLABY_USER_FOLLOWED_POSTS_PER_PAGE', 10), error_out=False)
    posts = pagination.items
    prev = None if not pagination.has_prev else url_for('api.get_user_followed_posts', page=page-1, _external=True)
    next = None if not pagination.has_next else url_for('api.get_user_followed_posts', page=page+1, _external=True)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })
    
@api.route('/users/<id>/comments')
def get_user_comments(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.comments.order_by(Comment.created_at.desc()).paginate(page, per_page=current_app.config.get('FLABY_USER_COMMENTS_PER_PAGE', 10), error_out=False)
    posts = pagination.items
    prev = None if not pagination.has_prev else url_for('api.get_user_comments', page=page-1, _external=True)
    next = None if not pagination.has_next else url_for('api.get_user_comments', page=page+1, _external=True)
    return jsonify({
        'comments': [comment.to_json() for comment in comments],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })