from flask import render_template, redirect, url_for, request, current_app
from flask_login import current_user, login_required
from ..models import User, Post, Comment, Permission
from . import main
from ..decrator import permission_required, admin_required
from .forms import ProfileEditForm, ProfileEditAdminForm, PostCreateForm, CommentCreateForm

@main.route('/')
def index():
    return render_template('index.html')
    
@main.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(user_name=username).first_or_404()
    return render_template('profile.html', user=user)
    
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
    
@main.route('/post-create', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.WRITE_ARTICLES)
def post_create():
    form = PostCreateForm()
    if form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        flash('A new post has been created.')
        return redirect(url_for('.post', id=post.id))
    return render_template('post_create.html', form=form)

@main.route('/post/<id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(post_id)
    form = CommentCreateForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          author=current_user._get_current_object(),
                          post=post)
        db.session.add(comment)
        db.session.commit()
        flash('You have created a new comment.')
        return redirect(url_for('.post', id=post_id))
    return render_template('post.html', post=post, form=form)
        
    
