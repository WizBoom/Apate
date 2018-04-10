#!/usr/bin/env python
from auth.app import Database, Util, FlaskApplication
from auth.models import *

Database.drop_all()
Database.create_all()

# Make admin
admin = Util.create_character(FlaskApplication.config['ADMIN_CHARACTER_ID'])
Util.create_all_corporations_in_alliance(admin.get_corp().get_alliance().id)

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
