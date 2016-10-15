from flask import Blueprint, render_template
from datetime import datetime

home = Blueprint('home',__name__,template_folder="templates")

@home.route('/')
@home.route('/home')
def show():
    """Renders the home page."""
    return render_template(
        'home/index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@home.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'home/contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@home.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'home/about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )
