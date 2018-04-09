from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for
from flask_login import current_user
from auth.models import *
from auth.admin.forms import *
from auth.shared import *

# Create and configure app
Application = Blueprint('admin', __name__, template_folder='templates', static_folder='static')


@Application.route('/', methods=['GET', 'POST'])
def index():
    permissions = Permission.query.all()

    addRoleForm = AddRoleForm()
    roleForms = list()
    for role in Role.query.all():
        roleForm = EditRoleForm()
        roleForm.name = role.name
        if request.method == 'GET':
            for permission in permissions:
                permForm = PermissionForm()
                permForm.permissionIndex = permission.id
                permForm.hasPermission = permission in role.permissions
                roleForm.permissions.append_entry(permForm)
        roleForms.append(roleForm)

    if request.method == 'POST':
        if request.form['btn'] == "AddRole" and addRoleForm.validate_on_submit():
            # Check if role with name already exists
            role = Role.query.filter_by(name=addRoleForm.roleName.data).first()

            # If role already exists, flash a message on screen
            if role:
                flash('Role {} already exists.'.format(role.name), 'warning')
            # Else create the role
            else:
                role = Role(addRoleForm.roleName.data)
                Database.session.add(role)
                Database.session.commit()
                flash('Succesfully added role {}.'.format(role.name), 'success')
                current_app.logger.info('{} created new role {}.'.format(current_user.name, role.name))
        elif request.form['btn'] == "EditRole":
            # Find the role that needs to be edited
            role = Role.query.filter_by(name=request.form['roleName']).first()
            # Double check if there is actually a role with that name
            # This should always be the case though
            if role:
                # Find linked form
                roleForm = None
                for rf in roleForms:
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

        elif request.form['btn'] == "RemoveRole":
            # Find the role that needs to be removed
            role = Role.query.filter_by(name=request.form['roleName']).first()

            # Double check if there is actually a role with that name
            # This should always be the case though
            if role:
                if not role.has_permission("admin"):
                    Database.session.delete(role)
                    Database.session.commit()
                    flash('Succesfully removed role {}.'.format(role.name), 'success')
                    current_app.logger.info('{} removed role {}.'.format(current_user.name, role.name))
                else:
                    flash('You cannot remove an admin role!', 'danger')
        return redirect(url_for('admin.index'))

    return render_template('index.html', permissions=permissions, addRoleForm=addRoleForm, roleForms=roleForms)
