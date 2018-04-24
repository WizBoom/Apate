#!/usr/bin/env python
from auth.shared import SharedInfo
from auth.app import Database, FlaskApplication
from auth.models import *

Database.drop_all()
Database.create_all()

# Create all corps in the alliance
SharedInfo['util'].create_all_corporations_in_alliance(FlaskApplication.config['ALLIANCE_ID'])

# Make admin
Admin = SharedInfo['util'].create_character(FlaskApplication.config['ADMIN_CHARACTER_ID'])

# Make admin role
AdminRole = Role('Admin')
Admin.roles.append(AdminRole)

# Make permissions
AdminPermission = Permission('admin')
CorpManagerPermission = Permission('corp_manager')
ReadMembershipPermission = Permission('read_membership')
EditMemberRolesPermission = Permission('edit_member_roles')
ReadApplicationsPermission = Permission('read_applications')
ReviewApplicationsPermission = Permission('review_applications')

# Link permissions
AdminRole.permissions.append(AdminPermission)
AdminRole.permissions.append(CorpManagerPermission)
AdminRole.permissions.append(ReadMembershipPermission)
AdminRole.permissions.append(ReadApplicationsPermission)
AdminRole.permissions.append(ReviewApplicationsPermission)
AdminRole.permissions.append(EditMemberRolesPermission)

Database.session.commit()
