from flask import render_template, redirect, url_for, request, current_app, flash
from flask_login import current_user, login_required
from ..models import User, Post, Comment, Permission
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
    pagination = Post.query.order_by(Post.created_at.desc()).paginate(page, per_page=current_app.config.get('FLABY_POSTS_PER_PAGE', 10), error_out=False)
    posts = pagination.items
    return render_template('index.html', posts=posts, pagination=pagination, form=form)
    
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
    return render_template('post_edit.html', form=form)

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
    return redirect(url_for('.comments_moderate', page=page))

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
    return redirect(url_for('.comments_moderate', page=page)) 

@main.route('/comment-delete/<id>')
@login_required
@permission_required(Permission.COMMENTS)
def comment_delete(id):
    comment = Comment.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment has been deleted.')
    return redirect(request.args.get('local') or url_for('.index'))