from flask import Blueprint, render_template
from flask_login import login_required

from . import PORTAL_TITLE


main = Blueprint("main", __name__)


@main.route('/')
def index():
    title = PORTAL_TITLE + ' - Home Page'
    return render_template('index.html', title=title)


@main.route('/resources')
@login_required
def resources():
    title = PORTAL_TITLE + ' - Home Page'
    return render_template('resources.html', title=title)
