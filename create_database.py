#!/usr/bin/env python
from auth.app import Database, Util, FlaskApplication
from auth.models import *

Database.drop_all()
Database.create_all()

# Create all corps in the alliance
Util.create_all_corporations_in_alliance(FlaskApplication.config['ALLIANCE_ID'])

# Make admin
admin = Util.create_character(FlaskApplication.config['ADMIN_CHARACTER_ID'])

# Make admin role
adminRole = Role('Admin')
admin.roles.append(adminRole)

# Make permissions
adminPermission = Permission('admin')
corpManagerPermission = Permission('corp_manager')

# Link permissions
adminRole.permissions.append(adminPermission)
adminRole.permissions.append(corpManagerPermission)

Database.session.commit()
