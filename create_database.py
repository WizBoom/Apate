#!/usr/bin/env python
from auth.app import Database, Util, FlaskApplication
from auth.models import *

Database.drop_all()
Database.create_all()

# Make admin
admin = Util.create_character(FlaskApplication.config['ADMIN_CHARACTER_ID'])

# Make admin role
adminRole = Role('Admin')
admin.roles.append(adminRole)

# Make permissions
adminPermission = Permission('admin')
readMemberPermission = Permission('read_members')
writeMemberPermission = Permission('write_members')
createSRPPermission = Permission('create_srp')
manageRolesPermission = Permission('manage_roles')
editDiscordPermission = Permission('edit_discord')

# Link permissions
adminRole.permissions.append(adminPermission)
adminRole.permissions.append(readMemberPermission)
adminRole.permissions.append(writeMemberPermission)
adminRole.permissions.append(createSRPPermission)
adminRole.permissions.append(manageRolesPermission)
adminRole.permissions.append(editDiscordPermission)

Database.session.commit()
