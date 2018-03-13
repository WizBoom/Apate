from flask import Blueprint, render_template


# Create and configure app
Application = Blueprint('admin', __name__, template_folder='templates', static_folder='static')


@Application.route('/')
def index():
    return render_template('index.html')
