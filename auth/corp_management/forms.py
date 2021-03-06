from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.widgets import TextArea


class EditCorpForm(FlaskForm):
    recruitment_status = SelectField('Recruitment Status', choices=[("open", "Open"), ("closed", "Closed")])
    description = StringField('Description', widget=TextArea())
