from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.widgets import TextArea


class EditCorpForm(FlaskForm):
    recruitmentStatus = SelectField('Recruitment Status', choices=[("open", "Open"), ("closed", "Closed")])
    description = StringField('Description', widget=TextArea())
