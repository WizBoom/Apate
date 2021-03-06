from flask import Blueprint, render_template, current_app, flash, url_for, redirect, request
from flask_login import login_required, current_user
from auth.models import Application as ApplicationModel, Corporation, Alliance, Character, Role
from auth.shared import Database, EveAPI, SharedInfo
from auth.decorators import needs_permission, alliance_required
from auth.hr.forms import *
from datetime import datetime
from sqlalchemy import func

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
        return redirect(url_for('hr.view_application', application_id=current_user.application.id))

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

    return render_template('hr/view_corp_applications.html', corporation=current_user.get_corp(),
        client_id=EveAPI['full_auth_preston'].client_id, client_secret=EveAPI['full_auth_preston'].client_secret, scopes=EveAPI['full_auth_preston'].scope)


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


@Application.route('/view_application/<int:application_id>', methods=['GET', 'POST'])
@login_required
def view_application(application_id):
    """Views an application with ID.

    Args:
        application_id (int): ID of the application.

    Returns:
        str: redirect to the appropriate url.
    """

    # Get user application.
    application = ApplicationModel.query.filter_by(id=application_id).first()
    isPersonalApplication = False

    # Redirect if application does not exist.
    if not application:
        flash("Application with ID {} is not present in the database.".format(str(application_id)), 'danger')
        current_app.logger.info("{} tried to view application with ID {} which does not exist in the database".format(current_user.name, str(application_id)))
        return redirect(url_for('hr.index'))

    # check if application is a personal application.
    if current_user.application and current_user.application.id == application_id:
        isPersonalApplication = True

    # Check if application corp is the user's corp.
    if not isPersonalApplication and application.corporation.id is not current_user.get_corp().id:
        flash('That application is not to your corp.', 'danger')
        current_app.logger.info("{} tried to view application which is not to their corporation.".format(current_user.name))
        return redirect(url_for('hr.index'))

    # Check if user is viewing a personal application or someone else's application.
    if not isPersonalApplication and not current_user.has_permission('read_applications'):
        flash("You do not have the required permission to view other people's applications.", "danger")
        current_app.logger.info("{} tried to illegally access someone else's application but didn't have the required read_applications permission.".format(current_user.name))
        return redirect(url_for('hr.index'))

    # Make application forms.
    removeApplicationForm = RemoveApplicationForm()
    editApplicationForm = EditNoteForm(notes=application.character.notes)

    # Removal of applications.
    if request.method == 'POST':
        # Check if notes were updated.
        if 'btn' not in request.form:
            if 'notes' in request.form and editApplicationForm.validate_on_submit():
                oldNote = application.character.notes
                application.character.notes = editApplicationForm.notes.data
                Database.session.commit()
                flash("Successfully updated note.", "success")
                current_app.logger.info("{} updated {}'s note from '{}' to '{}'.".format(current_user.name, application.character.name, oldNote, editApplicationForm.notes.data))
                return redirect(url_for('hr.view_application', application_id=application.id))

        # Check other button presses.
        if request.form['btn'] == "RemoveApplication":
            # Check if application is valid.
            if not removeApplicationForm.validate_on_submit():
                flash('Please make sure you provide a reason when removing an application.', 'danger')
                return redirect(url_for('hr.view_application', application_id=application.id))

            characterName = application.character.name
            corpName = application.corporation.name
            rejectionReason = removeApplicationForm.rejection_reason.data

            # Add note with rejection reason.
            # If there are already notes, add an enter.
            if application.character.notes:
                application.character.notes += "\n"
            application.character.notes += "Application removed ({}) by {}: {}".format(datetime.utcnow().strftime('%Y/%m/%d'), current_user.name, rejectionReason)

            Database.session.delete(application)
            Database.session.commit()

            flash("Successfully removed application of {} to {}.".format(characterName, corpName), 'success')
            current_app.logger.info("{} removed application of {} to {} with reason '{}'.".format(current_user.name, characterName, corpName, rejectionReason))
        elif request.form['btn'] == "RemovePersonalApplication":
            characterName = application.character.name
            corpName = application.corporation.name

            Database.session.delete(application)
            Database.session.commit()

            flash("Successfully removed application of {} to {}.".format(characterName, corpName), 'success')
            current_app.logger.info("{} removed application of {} to {}.".format(current_user.name, characterName, corpName))
        elif request.form['btn'] == "UpdateApplication":
            application.ready_accepted = not application.ready_accepted
            newStatus = "Ready to be accepted" if application.ready_accepted else "Being processed"
            Database.session.commit()
            flash("Successfully set {} application status to {}.".format(application.character.name, newStatus), 'success')
            current_app.logger.info("{} edited status of {} application to {}".format(current_user.name, application.character.name, newStatus))
            return redirect(url_for('hr.view_application', application_id=application.id))

        return redirect(url_for('hr.index'))

    return render_template('hr/view_application.html', application=application, personal_application=isPersonalApplication,
                           remove_form=removeApplicationForm, edit_form=editApplicationForm, discord_url=current_app.config['DISCORD_RECRUITMENT_INVITE'],
                           client_id=EveAPI['full_auth_preston'].client_id, client_secret=EveAPI['full_auth_preston'].client_secret, scopes=EveAPI['full_auth_preston'].scope)


@Application.route('/view_member/<int:member_id>', methods=['GET', 'POST'])
@login_required
@alliance_required()
@needs_permission('read_membership', 'View Member')
def view_member(member_id):
    """Views a member with ID.

    Args:
        member_id (int): ID of the member.

    Returns:
        str: redirect to the appropriate url.
    """

    # Get character and roles.
    character = Character.query.filter_by(id=member_id).first()
    roles = Role.query.all()
    mains = [main for main in Character.query.order_by(func.lower(Character.name)).all() if main.is_in_alliance]

    # Check if character exists.
    if not character:
        flash("Character with ID {} is not present in the database.".format(str(member_id)), 'danger')
        current_app.logger.info("{} tried to view member with ID {} which does not exist in the database".format(current_user.name, str(member_id)))
        return redirect(url_for('hr.index'))

    alts = [alt.name for alt in character.get_alts()]

    # Make note forms.
    editNoteForm = EditNoteForm(notes=character.notes)

    if request.method == 'POST':
        # Check if notes have been updated.
        if 'notes' in request.form and editNoteForm.validate_on_submit():
            oldNote = character.notes
            character.notes = editNoteForm.notes.data
            Database.session.commit()
            flash("Successfully updated note.", "success")
            current_app.logger.info("{} updated {}'s note from '{}' to '{}'.".format(current_user.name, character.name, oldNote, editNoteForm.notes.data))
        # Check the formtype.
        # Check if role toggle has been triggered.
        elif 'FormType' in request.form and request.form['FormType'] == "RoleToggle" and current_user.has_permission('corp_manager'):
            role = Role.query.filter_by(id=request.form['RoleId']).first()
            # If the user had the role, remove it.
            if role in character.roles:
                character.roles.remove(role)
                Database.session.commit()
                flash('Succesfully removed {} role from {}.'.format(role.name, character.name), 'success')
                current_app.logger.info('{} removed {} role from {}.'.format(current_user.name, role.name, character.name))
            # If the user didn't have the role, add it.
            else:
                character.roles.append(role)
                Database.session.commit()
                flash('Succesfully added {} role to {}.'.format(role.name, character.name), 'success')
                current_app.logger.info('{} added {} role to {}.'.format(current_user.name, role.name, character.name))
        # Check if main selection has been triggered.
        elif 'FormType' in request.form and request.form['FormType'] == "MainSelection" and current_user.has_permission('edit_member'):
            # Double check if main exist
            main = Character.query.filter_by(id=request.form['MainID']).first()
            if not main:
                flash('That main does not exist in the database.', 'danger')
                current_app.logger.warning("{} tried to edit {}'s main, but main with ID {} does not exist.".format(current_user.name, character.name, request.form['MainID']))
                return redirect(url_for('hr.view_member', member_id=character.id))

            oldMain = character.get_main().name
            character.main_id = request.form['MainID']
            Database.session.commit()
            flash('Successfully updated main from {} to {}.'.format(oldMain, character.get_main().name), 'success')
            current_app.logger.info("{} updated {}'s main from {} to {}".format(current_user.name, character.name, oldMain, character.get_main().name))
        # Check if deletion has been triggered.
        elif 'FormType' in request.form and request.form['FormType'] == "RemoveApplication" and current_user.has_permission('corp_manager'):
            Database.session.delete(character)
            Database.session.commit()
            flash('Sucessfully removed {}.'.format(character.name), 'success')
            current_app.logger.info("{} removed {} from the database.".format(current_user.name, character.name))
            return redirect(url_for('hr.index'))

        return redirect(url_for('hr.view_member', member_id=character.id))

    return render_template('hr/view_member.html', character=character, roles=roles, note_form=editNoteForm, alts=alts, mains=mains,
                           client_id=EveAPI['full_auth_preston'].client_id, client_secret=EveAPI['full_auth_preston'].client_secret, scopes=EveAPI['full_auth_preston'].scope)
