from flask import render_template, redirect, url_for, request, current_app, flash, make_response
from flask_login import current_user, login_required
from ..models import User, Post, Comment, Permission, Follow
from . import main
from ..decrator import permission_required, admin_required
from .forms import ProfileEditForm, ProfileEditAdminForm, PostCreateForm, CommentCreateForm
from .. import db

@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostCreateForm()
    if form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object(),
                    )
        db.session.add(post)
        db.session.commit()
        flash('A new post has been created.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.created_at.desc()).paginate(page, per_page=current_app.config.get('FLABY_POSTS_PER_PAGE', 10), error_out=False)
    posts = pagination.items
    return render_template('index.html', posts=posts, pagination=pagination, form=form, show_followed=show_followed)
    
@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp
    
@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp
    
@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(user_name=username).first_or_404()
    if not current_user.is_following(user):
        current_user.follow(user)
    flash('You are following %s.' % username)
    return redirect(url_for('.profile', username=username))
    
@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(user_name=username).first_or_404()
    if current_user.is_following(user):
        current_user.unfollow(user)
    flash('You are not following %s now.' % username)
    return redirect(url_for('.profile', username=username))
    
@main.route('/followed/<username>')
def followed(username):
    user = User.query.filter_by(user_name=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.order_by(Follow.created_at.desc()).paginate(page, per_page=current_app.config.get('FLABY_FOLLOWED_PER_PAGE', 10), error_out=False)
    follows = [{'user': item.followed, 'created_at': item.created_at} for item in pagination.items]
    return render_template('follows.html', pagination=pagination, follows=follows, user=user, title='Followed by %s' % username, endpoint='main.followed')

@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(user_name=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.order_by(Follow.created_at.desc()).paginate(page, per_page=current_app.config.get('FLABY_FOLLOWERS_PER_PAGE', 10), error_out=False)
    follows = [{'user': item.follower, 'created_at': item.created_at} for item in pagination.items]
    return render_template('follows.html', pagination=pagination, follows=follows, user=user, title='Followers of %s' % username, endpoint='main.followers')
    
@main.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(user_name=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.created_at.desc()).paginate(page, per_page=current_app.config.get('FLABY_POSTS_PER_PAGE', 10), error_out=False)
    posts = pagination.items
    return render_template('profile.html', user=user, posts=posts, pagination=pagination)
    
@main.route('/profile-edit', methods=['GET', 'POST'])
@login_required
def profile_edit():
    form = ProfileEditForm()
    if form.validate_on_submit():
        current_user.user_name = form.user_name.data
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.profile', username=current_user.user_name))
    form.user_name.data = current_user.user_name
    form.name.data = current_user.name 
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('profile_edit.html', form=form)
    
@main.route('/profile_edit/<id>', methods=['GET', 'POST'])
@login_required
@admin_required
def profile_edit_admin(id):
    user = User.query.get_or_404(id)
    form = ProfileEditAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.user_name = form.user_name.data
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get_or_404(form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('Profile Updated')
        return redirect(url_for('.profile', username=user.user_name))
    form.email.data = user.email
    form.user_name.data = user.user_name
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    return render_template('profile_edit_admin.html', form=form)
    
@main.route('/post-edit/<id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.WRITE_ARTICLES)
def post_edit(id):
    post = Post.query.get_or_404(id)
    form = PostCreateForm()
    if form.validate_on_submit():
        if post.body != form.body.data:
            post.body = form.body.data
            db.session.add(post)
            db.session.commit()
            flash('The post has been edited.')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('post_edit.html', form=form, post=post)

@main.route('/post/<id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentCreateForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          author=current_user._get_current_object(),
                          post=post)
        db.session.add(comment)
        db.session.commit()
        flash('You have created a new comment.')
        return redirect(url_for('.post', id=id)+'#comments')
    page = request.args.get('page', 1, type=int)
    pagination = post.comments.order_by(Comment.created_at.desc()).paginate(page, per_page=current_app.config.get('FLABY_COMMENTS_PER_PAGE', 5), error_out=False)
    comments = pagination.items
    return render_template('post.html', post=post, form=form, comments=comments, pagination=pagination)

@main.route('/post-delete/<id>')
@login_required
@permission_required(Permission.WRITE_ARTICLES)
def post_delete(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash('Post has been deleted.')
    return redirect(url_for('.index'))
    
@main.route('/post-enable/<id>')
@login_required
@admin_required
def post_enable(id):
    post = Post.query.get_or_404(id)
    post.disabled = False
    db.session.add(post)
    db.session.commit()
    flash('Post has been enabled.')
    return redirect(url_for('.index'))
    
@main.route('/post-disable/<id>')
@login_required
@admin_required
def post_disable(id):
    post = Post.query.get_or_404(id)
    post.disabled = True
    db.session.add(post)
    db.session.commit()
    flash('Post has been disabled.')
    return redirect(url_for('.index'))
    
@main.route('/comments-moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def comments_moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.created_at.desc()).paginate(page, per_page=current_app.config.get('FLABY_COMMENTS_PER_PAGE', 15), error_out=False)
    comments = pagination.items
    return render_template('comments_moderate.html', comments=comments, pagination=pagination)

@main.route('/comment-disabled/<id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def comment_disabled(id):
    comment = Comment.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    flash('The comment has been disabled.')
    return redirect(request.args.get('local') or url_for('.comments_moderate', page=page))

@main.route('/comment-enabled/<id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def comment_enabled(id):
    comment = Comment.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    flash('The comment has been enabled.')
    return redirect(request.args.get('local') or url_for('.comments_moderate', page=page)) 

@main.route('/comment-delete/<id>')
@login_required
@permission_required(Permission.COMMENTS)
def comment_delete(id):
    comment = Comment.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment has been deleted.')
    return redirect(request.args.get('local') or url_for('.index'))