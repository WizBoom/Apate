from flask import Blueprint, render_template, current_app, flash, url_for, redirect
from flask_login import login_required, current_user
from auth.models import Application as ApplicationModel, Corporation, Alliance
from auth.shared import Database

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

    # Get all corporations that are open for recruitment.
    openCorporations = [corp for corp in Alliance.query.filter_by(id=current_app.config["ALLIANCE_ID"]).first().corporations if corp.recruitment_open]

    return render_template('hr/index.html', open_corporations=openCorporations)


@Application.route('/apply/<int:corporation_id>')
def apply(corporation_id):
    """Apply page of a specific corporation.

    Args:
        corporation_id (int): Corporation id of the corporation to apply to.

    Returns:
        str: redirect to the appropriate url.
    """

    # Get corporation.
    corporation = Corporation.query.filter_by(id=corporation_id).first()

    # Check if corporation is open / in alliance
    if not corporation:
        flash("Corporation with ID {} is not present in the database.".format(str(corporation_id)), 'danger')
        current_app.logger.info("{} tried to apply to corporation with ID {} which does not exist in the database".format(current_user.name, str(corporation_id)))

        # If the user has an application already, redirect to the application. Else, go to the landing page.
        if current_user.application:
            return "Application"
        else:
            return redirect(url_for('hr.index'))

    # Check if character is not already in the corporation.
    if current_user.corp_id == corporation.id:
        flash("You're already in {}. If you'd like to add an alt, you can do so on your account management page.".format(corporation.name), 'danger')
        return redirect(url_for('landing'))

    # Check if corporation has open recruitment
    if not corporation.recruitment_open:
        flash("{} is not open for recruitment.".format(corporation.name), 'danger')
        current_app.logger.info("{} tried to apply to {} which does not have open recruitment.".format(current_user.name, corporation.name))
        return redirect(url_for('hr.index'))

    # Check if character already has an application.
    if current_user.application is not None:
        flash("You already have a pending application to {}. If you'd like to re-apply to another corporation, you can delete the current application.".format(
            current_user.application.corporation.name), 'danger')
        current_app.logger.info('{} tried to apply to {} but already had a pending application to {}'.format(current_user.name, corporation.name, current_user.application.corporation.name))
        return "Application"

    # Make application
    application = ApplicationModel(corporation)
    current_user.application = application
    Database.session.commit()

    flash("Successfully applied to {}.".format(corporation.name), 'success')
    current_app.logger.info('{} applied to {}.'.format(current_user.name, corporation.name))

    return redirect(url_for('hr.index'))
