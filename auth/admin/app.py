from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for
from flask_login import current_user, login_required
from auth.models import *
from auth.admin.forms import *
from auth.shared import EveAPI, SharedInfo
from auth.util import Util
from auth.decorators import needs_permission
# Create and configure app
Application = Blueprint('admin', __name__, template_folder='templates', static_folder='static')

# Util
Util = Util(
    current_app
)


@Application.route('/', methods=['GET', 'POST'])
@login_required
@needs_permission('admin', 'Admin Landing')
def index():
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
            Util.remove_role(request.form['roleName'], current_user.name, True)
        elif request.form['btn'] == "MakeCurrentCorp":
            edit_current_user_admin_corp(request.form['corpId'])
        return redirect(url_for('admin.index'))

    # Corporations
    # Get main alliance
    alliance = Alliance.query.filter_by(id=current_app.config["ALLIANCE_ID"]).first()

    return render_template('index.html', permissions=permissions, addRoleForm=addRoleForm,
                           roleForms=roleForms, corporations=alliance.corporations, corp_auth_url=EveAPI["corp_preston"].get_authorize_url())


@Application.route('/eve/corp/callback')
@login_required
@needs_permission('admin', 'Admin Corp Callback')
def eve_oauth_corp_callback():
    """Completes the EVE SSO CORP login. Here, a corp's ESI
    access & refresh token get updated.

    Args:
        None

    Returns:
        str: redirect to the appropriate url.
    """
    if 'error' in request.path:
        current_app.logger.error('Error in EVE SSO callback: ' + request.url)
        flash('There was an error in EVE\'s SSO response.', 'danger')
        return redirect(url_for('admin.index'))

    try:
        # Get character's corporation
        auth = EveAPI["corp_preston"].authenticate(request.args['code'])
        character_id = auth.whoami()['CharacterID']
        character_info = Util.make_esi_request("https://esi.tech.ccp.is/latest/characters/{}/?datasource=tranquility".format(str(character_id))).json()
        if not('alliance_id' in character_info and character_info['alliance_id'] == SharedInfo['alliance_id']):
            current_app.logger.info("{} tried to add a corporation ESI code with a character ({}) that isn't in alliance.".format(current_user.name, character_info['name']))
            flash('{} is not a member of the alliance and thus cannot provide a valid ESI code for a corporation!'.format(character_info['name']), 'danger')
            return redirect(url_for('admin.index'))

        # Get corporation
        corporation = Corporation.query.filter_by(id=character_info['corporation_id']).first()

        # Check if corporation exists
        if not corporation:
            current_app.logger.info("eve_oauth_corp_callback > corporation {} is not present in the database!".format(str(character_info['corporation_id'])))
            flash("The corporation is not present in the database, which shouldn't be possible. Contact the IT wizard!", 'danger')
            return redirect(url_for('admin.index'))

        corporation.access_token = auth.access_token
        corporation.refresh_token = auth.refresh_token
        Database.session.commit()
        current_app.logger.info("{} (using {}) succesfully updated ESI for {} with access token {} and refresh token {}".format(
            current_user.name, character_info['name'], corporation.name, str(auth.access_token), str(auth.refresh_token)))
        flash('Succesfully updated ESI for {}'.format(corporation.name), 'success')

        return redirect(url_for('admin.index'))
    except Exception as e:
        current_app.logger.error('ESI signing error: ' + str(e))
        flash('There was an authentication error signing you in.', 'danger')
        return redirect(url_for('admin.index'))

    flash(code, 'danger')
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
                permForm.hasPermission = permission in role.permissions
                roleForm.permissions.append_entry(permForm)
        roleForms.append(roleForm)
    return roleForms


def create_role_from_form(add_role_form):
    """Creates role based on an AddRoleForm

    Args:
        add_role_form (AddRoleForm): Forms to base role on.

    Returns:
        None
    """

    # Check if role with name already exists
    role = Role.query.filter_by(name=add_role_form.roleName.data).first()

    # If role already exists, flash a message on screen
    if role:
        flash('Role {} already exists.'.format(role.name), 'warning')
    # Else create the role
    else:
        role = Role(add_role_form.roleName.data)
        Database.session.add(role)
        Database.session.commit()
        flash('Succesfully added role {}.'.format(role.name), 'success')
        current_app.logger.info('{} created new role {}.'.format(current_user.name, role.name))


def edit_role_from_form(permissions, role_forms, role_name):
    """Edits role based on a list of EditRoleForm

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
                if roleForm.permissions[index].hasPermission.data:
                    # Add if not already in permission
                    if permission not in role.permissions:
                        role.permissions.append(permission)
                        addedPermissionNames.append(permission.name)
                else:
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
    """Edits current user's admin corporation

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