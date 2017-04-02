from flask import render_template, redirect, url_for, request, current_app
from flask_login import current_user, login_required
from ..models import User, Post, Comment
from . import main

@main.route('/')
def index():
    return render_template('index.html')
    
