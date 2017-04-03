from flask import request, render_template, url_for, redirect, current_app, flash, abort
from . import auth
from flask_login import current_user, login_required, login_user, logout_user
from ..models import User
from ..email import send_mail
from .. import db
from .forms import LoginForm, RegisterForm

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed and \
                reuqest.endpoint and request.endpoint[:5] == 'auth.' \
                and request.point != 'static':
            return redirect(url_for('.unconfirmed'))
            
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user is not None and user.verify_password(form.password.data):
            #user.is_active = True
            login_user(user, form.remember_me.data)
            flash('Authentication Succeed')
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Authentication Failed')
    return render_template('auth/login.html', form=form)
    
@auth.route('logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))
    
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(user_name=form.user_name.data,
                        email=form.email.data,
                        password=form.password1.data,
                        )
        db.session.add(new_user)
        db.session.commit()
        send_mail(new_user.email, 'Account Confirm', 'mail/auth/register', user=new_user, token=new_user.generate_confirm_token())
        flash('Your account has been successfully created, please check out your registered email and active your account.')
        return redirect(request.args.get('next') or url_for('main.index'))
    return render_template('auth/register.html', form=form)
    
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('Your account has been successfully actived.')
    else:
        flash('Confirm link is invalid or has expired.')
    return redirect(url_for('main.index'))
    
@auth.route('/confirm')
@login_required
def resend_mail():
    user = current_user._get_current_object()
    send_mail(new_user.email, 'Account Confirm', 'mail/auth/register', user=user, token=user.generate_confirm_token())
    flash('A confirmation email has been sent to your email box')
    return redirect(url_for('main.index'))
    

    