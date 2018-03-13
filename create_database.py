#!/usr/bin/env python
from auth.app import Database, Util, FlaskApplication
from auth.models import *

Database.drop_all()
Database.create_all()

# Make admin
admin = Util.create_character(FlaskApplication.config['ADMIN_CHARACTER_ID'])

# Make roles / permissions
adminRole = Role('Superadmin')
adminPermission = Permission('Superadmin')
adminRole.permissions.append(adminPermission)
admin.permissions.append(adminPermission)

Database.session.commit()
