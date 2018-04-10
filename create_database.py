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
testPermission = Permission('test')

# Link permissions
adminRole.permissions.append(adminPermission)
adminRole.permissions.append(testPermission)

Database.session.commit()
