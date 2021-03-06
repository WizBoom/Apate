from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, FieldList, FormField, HiddenField
from wtforms.validators import InputRequired


class AddRoleForm(FlaskForm):
    role_name = StringField('role', validators=[InputRequired()])


class PermissionForm(FlaskForm):
    # If we don't have this hidden field in de index, shit doesnt work for some reason
    hidden = HiddenField()
    has_permission = BooleanField()


class EditRoleForm(FlaskForm):
    name = StringField('role_name')
    permissions = FieldList(FormField(PermissionForm))
