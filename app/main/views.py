from flask import render_template, redirect, url_for, request, current_app
from flask_login import current_user, login_required
from ..models import User, Post, Comment, Permission
from . import main
from ..decrator import permission_required, admin_required
from .forms import ProfileEditForm, ProfileEditAdminForm

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
    
    
