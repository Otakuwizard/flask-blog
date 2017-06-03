from flask import url_for, jsonify, g, request, current_app
from . import api
from .. import db
from ..models import Blog, User, Tag
from app.exceptions import ValidationError
import json

@api.route('/blog/<id>/tags/get')
def blog_tags_get(id):
    blog = Blog.query.get_or_404(id)
    tags = Tag.query.all()
    blog_tags = blog.tags.all()
    blog_tags_name = [bt.name for bt in blog_tags]
    json_data = [t.to_json() for t in tags]
    for t in json_data:
        if t['name'] in blog_tags_name:
            t['selected'] = True
    return jsonify(json_data)

@api.route('/blog/<id>/tags/update')
def blog_tags_update(id):
    blog = Blog.query.get_or_404(id)
    print('Tags')
    print(request.get_data())
    selected_tags_str = request.args.get('s')
    selected_tags = selected_tags_str.split(',')
    tags = Tag.query.all()
    for tag in tags:
        blog.delete_tag(tag)
    db.session.commit()
    for st in selected_tags:
        stg = Tag.query.filter_by(name=st).first()
        blog.add_tag(stg)
    db.session.commit()
    blog_tags = blog.tags.all()
    return jsonify([bt.to_json() for bt in blog_tags])

