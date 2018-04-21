from flask import Blueprint, render_template, current_app, flash, url_for, redirect, request
from flask_login import login_required, current_user
from auth.models import Application as ApplicationModel, Corporation, Alliance
from auth.shared import Database, EveAPI, SharedInfo
from auth.decorators import needs_permission, alliance_required

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
    if not current_user.refresh_token or not current_user.access_token or not current_user.reddit:
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

    # Check if character already has an application
    if current_user.application is not None:
        flash("You already have an application.", 'danger')
        current_app.logger.info("{} tried to access application helper when they had an application.".format(current_user.name))
        return redirect(url_for('hr.view_application'))

    if request.method == 'POST':
        if request.form['btn'] == "RemoveESI":
            current_user.access_token = None
            current_user.refresh_token = None
            Database.session.commit()
            flash('Successfully removed ESI authorization.', 'success')
            current_app.logger.info('{} removed ESI authorization.'.format(current_user.name))
        elif request.form['btn'] == "RemoveReddit":
            oldReddit = current_user.reddit
            current_user.reddit = None
            flash('Successfully removed Reddit account', 'success')
            current_app.logger.info('{} removed Reddit account ({})'.format(current_user.name, oldReddit))

    return render_template('hr/application_helper.html', sso_url=EveAPI['full_auth_preston'].get_authorize_url() + "&state=" + request.url,
                           reddit_url=SharedInfo['reddit'].auth.url(['identity'], request.url, 'temporary'), discord_url=current_app.config['DISCORD_RECRUITMENT_INVITE'],
                           redirect_url=url_for('hr.apply', corporation_id=corporation_id))


@Application.route('/personal_application', methods=['GET', 'POST'])
@login_required
def personal_application():
    """Views the application of the current user.

    Args:
        None

    Returns:
        str: redirect to the appropriate url.
    """

    # Check if character has an application
    if current_user.application is None:
        flash("You have no pending application.", 'danger')
        current_app.logger.info("{} tried to access application when they didn't have an application.".format(current_user.name))
        return redirect(url_for('hr.index'))

    if request.method == 'POST':
        if request.form['btn'] == "RemoveApplication":
            Database.session.delete(current_user.application)
            Database.session.commit()
            return redirect(url_for('hr.index'))

    return render_template('hr/personal_application.html', discord_url=current_app.config['DISCORD_RECRUITMENT_INVITE'])


@Application.route('/view_corp_applications')
@login_required
@alliance_required()
@needs_permission('read_applications', 'View Corporation Applications')
def view_corp_applications():
    """Views all the applications to the current corp.

    Args:
        None

    Returns:
        str: redirect to the appropriate url.
    """

    return render_template('hr/view_corp_applications.html', corporation=current_user.get_corp())


@Application.route('/view_corp_members')
@login_required
@alliance_required()
@needs_permission('read_membership', 'View Corporation Members')
def view_corp_members():
    """Views all the members from the current corp.

    Args:
        None

    Returns:
        str: redirect to the appropriate url.
    """

    return render_template('hr/view_corp_members.html', corporation=current_user.get_corp())


@Application.route('/view_member/<int:member_id>')
@login_required
@alliance_required()
@needs_permission('read_applications', 'View Member')
def view_application(application_id):
    """Views a member with ID.

    Args:
        application_id (int): ID of the application.

    Returns:
        str: redirect to the appropriate url.
    """

    # Get application.
    application = ApplicationModel.query.filter_by(id=application_id).first()

    # Redirect if application does not exist.
    if not application:
        flash("Application with ID {} is not present in the database.".format(str(application_id)), 'danger')
        current_app.logger.info("{} tried to view application with ID {} which does not exist in the database".format(current_user.name, str(application_id)))
        return redirect(url_for('hr.index'))

    return render_template('hr/view_application.html', application=application)
