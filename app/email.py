from flask_mail import Message
from . import mail
from flask import current_app, render_template
from threading import Thread

def async_send_mail(app, msg):
    with app.app_context():
        mail.send(msg)
        
def send_mail(to, subject, template, **kw):
    app = current_app._get_current_object()
    msg = Message(app.config['FLABY_MAIL_SUBJECT_PREFIX') + ' ' + subject, sender=app.config['FLABY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kw)
    msg.html = render_template(template + '.html', **kw)
    thr = Thread(target=async_send_mail, args=[app, mag])
    thr.start()
    
    return thr