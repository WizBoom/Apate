from flask import Blueprint, render_template, current_app, flash, url_for, redirect, request
from flask_login import login_required, current_user
from auth.models import Application as ApplicationModel, Corporation, Alliance
from auth.shared import Database, EveAPI

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

    # If user already has an application, view that instead
    if current_user.application:
        return redirect(url_for('hr.view_application'))

    # Get all corporations that are open for recruitment.
    openCorporations = [corp for corp in Alliance.query.filter_by(id=current_app.config["ALLIANCE_ID"]).first().corporations if corp.recruitment_open]

    return render_template('hr/index.html', open_corporations=openCorporations)


@Application.route('/apply/<int:corporation_id>')
@login_required
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
            return redirect(url_for('hr.view_application'))
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
        return redirect(url_for('hr.view_application'))

    # Check if all necessary info is provided
    if not current_user.refresh_token or not current_user.access_token:
        return redirect(url_for('hr.application_help', corporation_id=corporation.id))

    # Make application
    application = ApplicationModel(corporation)
    current_user.application = application
    Database.session.commit()

    flash("Successfully applied to {}.".format(corporation.name), 'success')
    current_app.logger.info('{} applied to {}.'.format(current_user.name, corporation.name))

    return redirect(url_for('hr.index'))


@Application.route('/application_helper/<int:corporation_id>', methods=['GET', 'POST'])
@login_required
def application_help(corporation_id):
    """Application helper. This is used when the applying
    character has not provided all the necessary information
    yet. This will serve as a helper to guide them through
    all the information they have to provide.

    Args:
        corporation_id (int): Corporation id of the corporation to redirect to after all information has been filled out.

    Returns:
        str: redirect to the appropriate url.
    """

    if request.method == 'POST':
        if request.form['btn'] == "RemoveESI":
            current_user.access_token = None
            current_user.refresh_token = None
            Database.session.commit()

    return render_template('hr/application_helper.html', sso_url=EveAPI['full_auth_preston'].get_authorize_url() + "&state=" + request.url)


@Application.route('/view_application')
@login_required
def view_application():
    """Views the application of the current user.

    Args:
        None

    Returns:
        str: redirect to the appropriate url.
    """
    return render_template('hr/application.html')
