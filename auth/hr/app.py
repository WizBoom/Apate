from flask import Blueprint, render_template, current_app
from flask_login import login_required
from auth.models import *

# Create and configure app
Application = Blueprint('hr', __name__, template_folder='templates/hr', static_folder='static')


@Application.route('/')
@login_required
def index():
    """Landing page of the hr module

    Args:
        None

    Returns:
        str: redirect to the appropriate url.
    """

    # Get all corporations that are open for recruitment
    openCorporations = [corp for corp in Alliance.query.filter_by(id=current_app.config["ALLIANCE_ID"]).first().corporations if corp.recruitment_open]

    return render_template('hr/index.html', open_corporations=openCorporations)
