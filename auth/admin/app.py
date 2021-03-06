from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for
from flask_login import current_user, login_required
from auth.models import *
from auth.admin.forms import *
from auth.shared import EveAPI, SharedInfo
from auth.decorators import needs_permission, alliance_required

# Create and configure app
Application = Blueprint('admin', __name__, template_folder='templates/admin', static_folder='static')


@Application.route('/', methods=['GET', 'POST'])
@login_required
@alliance_required()
@needs_permission('admin', 'Admin Landing')
def index():
    """Landing page of the admin module.

    Args:
        None

    Returns:
        str: redirect to the appropriate url.
    """
    permissions = Permission.query.all()

    # Roles
    addRoleForm = AddRoleForm()
    roleForms = create_edit_role_forms(permissions, request.method == 'GET')

    if request.method == 'POST':
        if request.form['btn'] == "AddRole" and addRoleForm.validate_on_submit():
            create_role_from_form(addRoleForm)
        elif request.form['btn'] == "EditRole":
            edit_role_from_form(permissions, roleForms, request.form['roleName'])
        elif request.form['btn'] == "RemoveRole":
            SharedInfo['util'].remove_role(request.form['roleName'], current_user.name, True)
        elif request.form['btn'] == "MakeCurrentCorp":
            edit_current_user_admin_corp(request.form['corpId'])
        return redirect(url_for('admin.index'))

    # Corporations
    # Get main alliance
    alliance = Alliance.query.filter_by(id=current_app.config["ALLIANCE_ID"]).first()

    return render_template('admin/index.html', permissions=permissions, add_role_form=addRoleForm,
                           role_forms=roleForms, corporations=alliance.corporations, corp_auth_url=EveAPI["corp_preston"].get_authorize_url())


@Application.route('/sync/')
@login_required
@alliance_required()
@needs_permission('admin', 'Admin Sync')
def sync():
    """Page that syncs the whole database.

    Args:
        None

    Returns:
        str: redirect to the appropriate url.
    """
    current_app.logger.info("Starting sync ...")

    statusCode = sync_database_membership()
    if statusCode != 200:
        flash("Sync failed on database sync with error code {}".format(str(statusCode)), 'danger')
        current_app.logger.info("Sync failed.")
        return redirect(url_for('admin.index'))

    alliance = Alliance.query.filter_by(id=current_app.config["ALLIANCE_ID"]).first()

    for corporation in alliance.corporations:
        if corporation.refresh_token:
            statusCode = sync_corp_membership(corporation)
            if statusCode != 200:
                flash("Sync failed on {} sync with error code {}".format(corporation.name, str(statusCode)), 'danger')
                current_app.logger.info("Sync failed.")
                return redirect(url_for('admin.index'))

    current_app.logger.info("Sync completed successfully.")
    flash('Sync completed successfully.', 'success')
    return redirect(url_for('admin.index'))


def create_edit_role_forms(permissions, create_permissions):
    """Creates the edit role forms with the correct permissions.

    Args:
        permissions (List<Permission>): List of all the permissions.
        create_permissions (bool): Create a list of all the permissions and attach to the form if true.

    Returns:
        list<EditRoleForm>: List of all the edit role forms.
    """

    roleForms = list()
    for role in Role.query.all():
        roleForm = EditRoleForm()
        roleForm.name = role.name
        if create_permissions:
            for permission in permissions:
                permForm = PermissionForm()
                permForm.permissionIndex = permission.id
                permForm.has_permission = permission in role.permissions
                roleForm.permissions.append_entry(permForm)
        roleForms.append(roleForm)
    return roleForms


def create_role_from_form(add_role_form):
    """Creates role based on an AddRoleForm.

    Args:
        add_role_form (AddRoleForm): Forms to base role on.

    Returns:
        None
    """

    # Check if role with name already exists
    role = Role.query.filter_by(name=add_role_form.role_name.data).first()

    # If role already exists, flash a message on screen
    if role:
        flash('Role {} already exists.'.format(role.name), 'warning')
    # Else create the role
    else:
        role = Role(add_role_form.role_name.data)
        Database.session.add(role)
        Database.session.commit()
        flash('Succesfully added role {}.'.format(role.name), 'success')
        current_app.logger.info('{} created new role {}.'.format(current_user.name, role.name))


def edit_role_from_form(permissions, role_forms, role_name):
    """Edits role based on a list of EditRoleForm.

    Args:
        permissions (List<Permission>): List of all permissions.
        role_forms (List<EditRoleForm>): List of all the EditRoleForms.
        role_name (string): Name of the role to edit.

    Returns:
        None
    """

    # Find the role that needs to be edited
    role = Role.query.filter_by(name=role_name).first()
    # Double check if there is actually a role with that name
    # This should always be the case though
    if role:
        # Find linked form
        roleForm = None
        for rf in role_forms:
            if rf.name == role.name:
                roleForm = rf
                break
        # Double check if there is a linked form
        if roleForm:
            # Keep track of names for logging
            addedPermissionNames = []
            removedPermissionNames = []
            for index, permission in enumerate(permissions):
                # Check if role has permission now
                if roleForm.permissions[index].has_permission.data:
                    # Add if not already in permission
                    if permission not in role.permissions:
                        role.permissions.append(permission)
                        addedPermissionNames.append(permission.name)
                elif permission.name != "admin":
                    # Remove if already in permission
                    if permission in role.permissions:
                        role.permissions.remove(permission)
                        removedPermissionNames.append(permission.name)

            Database.session.commit()
            flash('Succesfully edited role {} by adding the following permissions: "{}" and by removing the following permissions: "{}".'.format(
                role.name, ", ".join(addedPermissionNames), ", ".join(removedPermissionNames)), 'success')
            current_app.logger.info('{} edited role {} by adding the following permissions: "{}" and by removing the following permissions: "{}".'.format(
                current_user.name, role.name, ", ".join(addedPermissionNames), ", ".join(removedPermissionNames)))


def edit_current_user_admin_corp(corp_id):
    """Edits current user's admin corporation.

    Args:
        corp_id (int): ID of the new corporation.

    Returns:
        None
    """

    # Check if the corporation is actually in the alliance.
    corporation = Corporation.query.filter_by(id=corp_id).first()
    setCorp = corp_id

    if not corporation:
        # Reset to player's corporation
        current_user.admin_corp_id = current_user.corp_id
        setCorp = current_user.corp_id
        flash('Could not find corporation with id {} in database, resetted to your own corporation ({}) instead.'.format(str(corp_id), current_user.corp_id), 'warning')
    else:
        current_user.admin_corp_id = corporation.id
        flash('Set current corporation to {}.'.format(str(corporation.name)), 'success')

    current_app.logger.info("Set {}'s admin corporation ID to {}.".format(current_user.name, str(setCorp)))
    Database.session.commit()


def sync_database_membership():
    """Updates all the members in the database.

    Args:
        None

    Returns:
        int: status code
    """

    current_app.logger.info("Syncing database membership ...")

    # Loop over all characters in the database
    for character in Character.query.all():
        # Get character information
        characterPayload = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/characters/{}/?datasource=tranquility".format(str(character.id)))
        characterJson = characterPayload.json()

        if characterPayload.status_code != 200:
            current_app.logger.error('sync_database_membership > Sync failed with error {}: {}'.format(str(characterPayload.status_code, characterJson['error'])))
            current_app.logger.info('Database membership sync failed.')
            return characterPayload.status_code

        SharedInfo['util'].update_character_corporation(character, characterJson['corporation_id'])

    current_app.logger.info("Successfully synced database membership.")
    return 200


def sync_corp_membership(corporation):
    """Updates all the members in a corporation.

    Args:
        corporation (Corporation): Corporation to sync.

    Returns:
        int: status code
    """

    current_app.logger.info("Syncing {} membership ...".format(corporation.name))

    # Update access token
    EveAPI["corp_preston"].refresh_token = corporation.refresh_token
    corporation.access_token = EveAPI["corp_preston"]._get_access_from_refresh()[0]

    # Get members in corp
    membersPayload = SharedInfo['util'].make_esi_request("https://esi.tech.ccp.is/latest/corporations/{}/members/?datasource=tranquility&token={}".format(
        str(corporation.id), corporation.access_token))
    membersJson = membersPayload.json()

    if membersPayload.status_code != 200:
        current_app.logger.error('sync_corp_membership > Sync failed with error {}: {}'.format(str(membersPayload.status_code, membersJson['error'])))
        current_app.logger.info('Corp membership sync failed.')
        return membersPayload.status_code

    # Loop over all corp members
    for member in membersJson:
        # Check if character already exists in database
        character = Character.query.filter_by(id=member).first()

        # If not, create it
        if not character:
            character = SharedInfo['util'].create_character(member)

    current_app.logger.info("Successfully synced {} membership.".format(corporation.name))
    return 200
