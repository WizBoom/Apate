from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for
from flask_login import current_user
from auth.models import *
from auth.admin.forms import *
from auth.shared import *
from auth.util import Util

# Create and configure app
Application = Blueprint('admin', __name__, template_folder='templates', static_folder='static')

# Util
Util = Util(
    current_app
)


@Application.route('/', methods=['GET', 'POST'])
def index():
    if not current_user.has_permission("admin"):
        return redirect(current_app.config['BASE_URL'])

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
        return redirect(url_for('admin.index'))

    return render_template('index.html', permissions=permissions, addRoleForm=addRoleForm, roleForms=roleForms)


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
